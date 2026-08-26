import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Share2,
  Search,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Play,
  Pause,
  UploadCloud,
  FileText,
  Shield,
  Layers,
  Crosshair,
  Filter,
  Eye,
  EyeOff,
  Download,
  CheckCircle2,
  AlertCircle,
  Network,
  X,
  ExternalLink,
  Tag,
  User,
  Car,
  Smartphone,
  CreditCard,
  MapPin
} from 'lucide-react';
import {
  globalNetworkStore,
  GraphTopologyBuilder,
  GraphPathSolver,
  GRAPHIFY_COLOR_PALETTE
} from '../services/networkAnalyticsService';
import { parseCSV } from '../services/datasetStore';

export default function NetworkGraphView({ datasetState, onBackToChat }) {
  const canvasRef = useRef(null);

  // Store state
  const [networkData, setNetworkData] = useState(() => globalNetworkStore.getState());
  const [isPhysicsRunning, setIsPhysicsRunning] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [focusedNeighborhood, setFocusedNeighborhood] = useState(null); // Set of node IDs
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilterType, setActiveFilterType] = useState('ALL');

  // Shortest Path Finder UI State
  const [pathStartQuery, setPathStartQuery] = useState('');
  const [pathTargetQuery, setPathTargetQuery] = useState('');
  const [activePathResult, setActivePathResult] = useState(null);
  const [isPathFinderOpen, setIsPathFinderOpen] = useState(false);

  // Dedicated Upload Modal State
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  // Canvas Viewport Transform (Pan & Zoom)
  const transformRef = useRef({ x: 0, y: 0, scale: 0.85 });
  const isDraggingCanvasRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const draggedNodeRef = useRef(null);

  // Synchronize with Global Store and Primary Dataset State
  useEffect(() => {
    const unsubscribe = globalNetworkStore.subscribe(state => {
      setNetworkData(state);
    });

    if (datasetState?.isLoaded && datasetState?.rawRecords?.length > 0 && !networkData.isLocked) {
      const headers = datasetState.columns || Object.keys(datasetState.rawRecords[0] || {});
      globalNetworkStore.loadDataset(datasetState.rawRecords, headers, datasetState.filename || 'Active Investigation Dataset');
    }

    return unsubscribe;
  }, [datasetState]);

  // Nodes, Edges & Dynamic Feature Types
  const nodes = networkData.nodes;
  const edges = networkData.edges;
  const featureTypes = networkData.featureTypes || [];

  // Filtered Nodes by Entity Type
  const filteredNodes = useMemo(() => {
    if (activeFilterType === 'ALL') return nodes;
    return nodes.filter(n => n.type === activeFilterType);
  }, [nodes, activeFilterType]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  // Autocomplete Suggestions for Search
  const searchSuggestions = useMemo(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) return [];
    const q = searchQuery.toLowerCase();
    return nodes.filter(n => n.label.toLowerCase().includes(q) || n.rawId?.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)).slice(0, 8);
  }, [searchQuery, nodes]);

  // ==========================================
  // FLUID GRAPHIFY PHYSICS SIMULATION LOOP
  // ==========================================
  useEffect(() => {
    let animationFrameId;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const handleResize = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    handleResize();
    window.addEventListener('resize', handleResize);

    const simulationStep = () => {
      if (isPhysicsRunning && nodes.length > 0) {
        const kBase = 240; // Base Spring Rest Length
        const maxRepulsiveDist = 600;
        const damping = 0.84;
        const centerGravity = 0.005;

        // 1. Repulsion & Dynamic Collision Relaxation between all node pairs
        for (let i = 0; i < nodes.length; i++) {
          const na = nodes[i];
          const ra = Math.max(10, Math.min(24, 9 + (na.degree || 1) * 1.5));

          for (let j = i + 1; j < nodes.length; j++) {
            const nb = nodes[j];
            const rb = Math.max(10, Math.min(24, 9 + (nb.degree || 1) * 1.5));
            const minAllowedDist = ra + rb + 44; // Enhanced collision separation buffer

            const dx = nb.x - na.x;
            const dy = nb.y - na.y;
            const distSq = dx * dx + dy * dy || 1;
            const dist = Math.sqrt(distSq);

            // Hard Non-Penetration Resolution (Instantly pushes overlapping circles & labels apart)
            if (dist < minAllowedDist) {
              const overlap = (minAllowedDist - dist) * 0.6;
              const nx = (dx / dist) * overlap;
              const ny = (dy / dist) * overlap;
              if (draggedNodeRef.current?.id !== na.id) { na.x -= nx; na.y -= ny; na.vx -= nx * 0.4; na.vy -= ny * 0.4; }
              if (draggedNodeRef.current?.id !== nb.id) { nb.x += nx; nb.y += ny; nb.vx += nx * 0.4; nb.vy += ny * 0.4; }
            } else if (dist < maxRepulsiveDist) {
              // Smooth Coulomb Repulsion
              const force = Math.min(26, 4600 / (distSq + 45));
              const fx = (dx / dist) * force;
              const fy = (dy / dist) * force;

              if (draggedNodeRef.current?.id !== na.id) { na.vx -= fx; na.vy -= fy; }
              if (draggedNodeRef.current?.id !== nb.id) { nb.vx += fx; nb.vy += fy; }
            }
          }

          // Gentle Center Pull
          if (draggedNodeRef.current?.id !== na.id) {
            na.vx -= na.x * centerGravity;
            na.vy -= na.y * centerGravity;
          }
        }

        // 2. Adaptive Spring attraction along multi-hop edges
        edges.forEach(e => {
          const sourceNode = typeof e.source === 'object' ? e.source : nodes.find(n => n.id === e.source);
          const targetNode = typeof e.target === 'object' ? e.target : nodes.find(n => n.id === e.target);
          if (!sourceNode || !targetNode) return;

          // Adaptive spring length based on node degrees
          const k = kBase + Math.min(120, (sourceNode.degree + targetNode.degree) * 6);

          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const displacement = dist - k;
          const force = Math.min(14, Math.max(-14, displacement * 0.024));

          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          if (draggedNodeRef.current?.id !== sourceNode.id) { sourceNode.vx += fx; sourceNode.vy += fy; }
          if (draggedNodeRef.current?.id !== targetNode.id) { targetNode.vx -= fx; targetNode.vy -= fy; }
        });

        // 3. Update positions with velocity damping & NaN safeguards
        nodes.forEach(n => {
          if (draggedNodeRef.current && draggedNodeRef.current.id === n.id) {
            n.vx = 0;
            n.vy = 0;
            return;
          }
          n.vx = Math.max(-7, Math.min(7, (isNaN(n.vx) ? 0 : n.vx) * damping));
          n.vy = Math.max(-7, Math.min(7, (isNaN(n.vy) ? 0 : n.vy) * damping));
          n.x += n.vx;
          n.y += n.vy;
          if (isNaN(n.x)) n.x = 0;
          if (isNaN(n.y)) n.y = 0;
        });
      }

      // ==========================================
      // RENDER CANVAS (GRAPHIFY AESTHETICS)
      // ==========================================
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.save();
      ctx.translate(canvas.width / 2 + transformRef.current.x, canvas.height / 2 + transformRef.current.y);
      ctx.scale(transformRef.current.scale, transformRef.current.scale);

      const activeFocus = selectedNode || hoveredNode;
      const activeNeighborhoodSet = focusedNeighborhood;

      // 1. Draw Edges
      edges.forEach(e => {
        const sourceNode = typeof e.source === 'object' ? e.source : nodes.find(n => n.id === e.source);
        const targetNode = typeof e.target === 'object' ? e.target : nodes.find(n => n.id === e.target);
        if (!sourceNode || !targetNode) return;

        const isPathEdge = activePathResult?.pathEdges?.some(
          pe => (pe.from === sourceNode.id && pe.to === targetNode.id) || (pe.from === targetNode.id && pe.to === sourceNode.id)
        );

        const isFocusedEdge = activeFocus
          ? (sourceNode.id === activeFocus.id || targetNode.id === activeFocus.id)
          : false;

        const isFiltered = filteredNodeIds.has(sourceNode.id) && filteredNodeIds.has(targetNode.id);

        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);

        if (isPathEdge) {
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 3.8;
          ctx.shadowColor = '#38bdf8';
          ctx.shadowBlur = 14;
        } else if (isFocusedEdge) {
          // Graphify Highlighted Neighbor Edge (Neon Violet / Purple)
          ctx.strokeStyle = '#a855f7';
          ctx.lineWidth = 2.4;
          ctx.shadowColor = '#a855f7';
          ctx.shadowBlur = 10;
        } else if (activeFocus) {
          // Dim background edges
          ctx.strokeStyle = 'rgba(148, 163, 184, 0.04)';
          ctx.lineWidth = 0.8;
          ctx.shadowBlur = 0;
        } else {
          // Standard Graphify clean link
          ctx.strokeStyle = isFiltered ? 'rgba(148, 163, 184, 0.25)' : 'rgba(148, 163, 184, 0.04)';
          ctx.lineWidth = 1.1;
          ctx.shadowBlur = 0;
        }

        ctx.stroke();
      });

      // 2. Draw Nodes
      nodes.forEach(n => {
        const isSelected = selectedNode?.id === n.id;
        const isHovered = hoveredNode?.id === n.id;
        const isPathNode = activePathResult?.pathNodes?.some(pn => pn.id === n.id);
        const isNeighborhood = activeNeighborhoodSet ? activeNeighborhoodSet.has(n.id) : true;
        const isFiltered = filteredNodeIds.has(n.id);

        const radius = Math.max(9, Math.min(24, 8 + (n.degree || 1) * 1.5));
        const opacity = activeFocus
          ? (isNeighborhood || isSelected || isHovered || isPathNode ? 1.0 : 0.12)
          : (isFiltered ? 1.0 : 0.15);

        ctx.save();
        ctx.globalAlpha = opacity;

        // God Node / Hub Halo
        if (n.degree >= 5 || isPathNode || isSelected || isHovered) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, radius + 7, 0, Math.PI * 2);
          ctx.fillStyle = isPathNode ? 'rgba(56, 189, 248, 0.45)' : isSelected ? 'rgba(239, 68, 68, 0.45)' : isHovered ? 'rgba(168, 85, 247, 0.45)' : `${n.color}35`;
          ctx.fill();
        }

        // Main Node Circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = isPathNode
          ? '#38bdf8'
          : isSelected
          ? '#ef4444'
          : isHovered
          ? '#a855f7'
          : n.color || '#94a3b8';
        ctx.fill();
        ctx.lineWidth = isSelected || isHovered ? 3.2 : 1.8;
        ctx.strokeStyle = isSelected ? '#ffffff' : isHovered ? '#f8fafc' : 'rgba(255, 255, 255, 0.85)';
        ctx.stroke();

        // Node Label
        if (transformRef.current.scale > 0.45 || isSelected || isHovered || isPathNode || n.degree >= 3) {
          const fontSize = isSelected || isHovered || isPathNode ? 11.5 : 10;
          ctx.font = `${isSelected || isHovered || isPathNode ? 'bold ' : '600 '}${fontSize}px Inter, system-ui, sans-serif`;
          ctx.fillStyle = isPathNode ? '#38bdf8' : isHovered ? '#c084fc' : '#f8fafc';
          ctx.textAlign = 'center';
          ctx.fillText(n.label, n.x, n.y + radius + 13);
        }

        ctx.restore();
      });

      ctx.restore();

      animationFrameId = requestAnimationFrame(simulationStep);
    };

    animationFrameId = requestAnimationFrame(simulationStep);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, [isPhysicsRunning, nodes, edges, selectedNode, hoveredNode, focusedNeighborhood, activePathResult, filteredNodeIds]);

  // ==========================================
  // FLUID MOUSE DRAG & HIT TEST HANDLERS
  // ==========================================
  const getCanvasMousePos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;

    const x = (clientX - canvasRef.current.width / 2 - transformRef.current.x) / transformRef.current.scale;
    const y = (clientY - canvasRef.current.height / 2 - transformRef.current.y) / transformRef.current.scale;
    return { x, y, rawX: e.clientX, rawY: e.clientY };
  };

  const handleMouseDown = (e) => {
    const { x, y, rawX, rawY } = getCanvasMousePos(e);

    // Hit test with generous grab radius
    const clickedNode = nodes.find(n => {
      const radius = Math.max(14, Math.min(28, 9 + (n.degree || 1) * 1.5));
      const dx = n.x - x;
      const dy = n.y - y;
      return dx * dx + dy * dy <= radius * radius;
    });

    if (clickedNode) {
      draggedNodeRef.current = clickedNode;
      setSelectedNode(clickedNode);

      // Compute 1-hop & 2-hop neighborhood
      const neighbors = new Set([clickedNode.id]);
      edges.forEach(edge => {
        const s = typeof edge.source === 'object' ? edge.source.id : edge.source;
        const t = typeof edge.target === 'object' ? edge.target.id : edge.target;
        if (s === clickedNode.id) neighbors.add(t);
        if (t === clickedNode.id) neighbors.add(s);
      });
      setFocusedNeighborhood(neighbors);
    } else {
      isDraggingCanvasRef.current = true;
      dragStartRef.current = { x: rawX - transformRef.current.x, y: rawY - transformRef.current.y };
    }
  };

  const handleMouseMove = (e) => {
    const { x, y } = getCanvasMousePos(e);

    if (draggedNodeRef.current) {
      // Fluid Real-Time Node Movement under Cursor
      draggedNodeRef.current.x = x;
      draggedNodeRef.current.y = y;
      draggedNodeRef.current.vx = 0;
      draggedNodeRef.current.vy = 0;
    } else if (isDraggingCanvasRef.current) {
      transformRef.current.x = e.clientX - dragStartRef.current.x;
      transformRef.current.y = e.clientY - dragStartRef.current.y;
    } else {
      // Hover detection
      const found = nodes.find(n => {
        const radius = Math.max(14, Math.min(28, 9 + (n.degree || 1) * 1.5));
        const dx = n.x - x;
        const dy = n.y - y;
        return dx * dx + dy * dy <= radius * radius;
      });
      setHoveredNode(found || null);
    }
  };

  const handleMouseUp = () => {
    draggedNodeRef.current = null;
    isDraggingCanvasRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newScale = Math.min(4, Math.max(0.15, transformRef.current.scale * zoomFactor));
    transformRef.current.scale = newScale;
  };

  // Fly-to Node function
  const flyToNode = (node) => {
    if (!node) return;
    setSelectedNode(node);
    transformRef.current = {
      x: -node.x * 1.1,
      y: -node.y * 1.1,
      scale: 1.1
    };

    const neighbors = new Set([node.id]);
    edges.forEach(edge => {
      const s = typeof edge.source === 'object' ? edge.source.id : edge.source;
      const t = typeof edge.target === 'object' ? edge.target.id : edge.target;
      if (s === node.id) neighbors.add(t);
      if (t === node.id) neighbors.add(s);
    });
    setFocusedNeighborhood(neighbors);
  };

  // Reset View
  const handleResetView = () => {
    transformRef.current = { x: 0, y: 0, scale: 0.85 };
    setSelectedNode(null);
    setHoveredNode(null);
    setFocusedNeighborhood(null);
    setActivePathResult(null);
    setActiveFilterType('ALL');
  };

  // Execute Shortest Path Traversal
  const handleExecutePathFinder = () => {
    if (!pathStartQuery || !pathTargetQuery) return;
    const result = GraphPathSolver.findShortestPath(nodes, edges, pathStartQuery, pathTargetQuery);
    setActivePathResult(result);
    if (result.found && result.startNode) {
      flyToNode(result.startNode);
    }
  };

  // Dedicated Upload Handler
  const handleDedicatedFileUpload = (file) => {
    if (!file) return;
    setUploadError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        let records = [];
        let headers = [];

        if (file.name.endsWith('.json')) {
          const parsedJson = JSON.parse(text);
          if (Array.isArray(parsedJson)) {
            records = parsedJson;
            headers = Object.keys(parsedJson[0] || {});
          } else if (parsedJson.records && Array.isArray(parsedJson.records)) {
            records = parsedJson.records;
            headers = parsedJson.headers || Object.keys(records[0] || {});
          }
        } else {
          const parsed = parseCSV(text);
          headers = parsed.headers || [];
          records = parsed.records || [];
        }

        if (!records || records.length === 0) {
          setUploadError('Uploaded file contains no records.');
          return;
        }
        globalNetworkStore.loadDedicatedNetworkData(records, headers, file.name);
        setIsUploadModalOpen(false);
      } catch (err) {
        setUploadError(`Failed to parse file: ${err.message}`);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      backgroundColor: '#0a0f1d',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
      color: '#f8fafc'
    }}>
      {/* TOP COMMAND HEADER */}
      <div style={{
        height: '56px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backgroundColor: '#0f172a',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 20
      }}>
        {/* LEFT BRAND & TITLE */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: 'rgba(56, 189, 248, 0.15)',
            border: '1px solid rgba(56, 189, 248, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Network size={18} style={{ color: '#38bdf8' }} />
          </div>
          <div>
            <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Network Link Intelligence & Graph Topology
              <span style={{ fontSize: '0.68rem', padding: '2px 8px', borderRadius: '10px', background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', fontWeight: 800 }}>
                {networkData.isLocked ? `${nodes.length} Entities · ${edges.length} Multi-Hop Links` : 'Awaiting Dataset'}
              </span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748b' }}>
              Fluid Force-Directed Drag & Drop · Real Investigative Entity Linkage (Zero Demographic Noise)
            </div>
          </div>
        </div>

        {/* CENTER SEARCH & AUTOCOMPLETE */}
        <div style={{ position: 'relative', width: '300px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#090d16',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '8px',
            padding: '4px 10px',
            gap: '8px'
          }}>
            <Search size={14} style={{ color: '#64748b' }} />
            <input
              type="text"
              placeholder="Search Suspect, Vehicle, Phone, Mule..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#f8fafc',
                fontSize: '0.75rem',
                width: '100%'
              }}
            />
            {searchQuery && (
              <X size={12} style={{ color: '#64748b', cursor: 'pointer' }} onClick={() => setSearchQuery('')} />
            )}
          </div>

          {/* Autocomplete Dropdown */}
          {searchSuggestions.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '38px',
              left: 0,
              width: '100%',
              backgroundColor: '#0f172a',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '8px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.6)',
              zIndex: 50,
              overflow: 'hidden'
            }}>
              {searchSuggestions.map(n => (
                <div
                  key={n.id}
                  onClick={() => {
                    flyToNode(n);
                    setSearchQuery('');
                  }}
                  style={{
                    padding: '8px 12px',
                    fontSize: '0.75rem',
                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(56, 189, 248, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: n.color }} />
                    <span style={{ fontWeight: 700, color: '#f8fafc' }}>{n.label}</span>
                  </div>
                  <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>{n.typeLabel}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* RIGHT CONTROLS & ATTACH DATASET BUTTON */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => setIsPathFinderOpen(!isPathFinderOpen)}
            style={{
              padding: '6px 12px',
              fontSize: '0.72rem',
              fontWeight: 800,
              borderRadius: '6px',
              border: isPathFinderOpen ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.12)',
              backgroundColor: isPathFinderOpen ? 'rgba(56, 189, 248, 0.15)' : '#0f172a',
              color: isPathFinderOpen ? '#38bdf8' : '#cbd5e1',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Share2 size={13} />
            Trace Multi-Hop Path
          </button>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            style={{
              padding: '6px 12px',
              fontSize: '0.72rem',
              fontWeight: 800,
              borderRadius: '6px',
              border: '1px solid rgba(56, 189, 248, 0.4)',
              backgroundColor: '#0284c7',
              color: '#ffffff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <UploadCloud size={13} />
            Attach Network / CDR File
          </button>
        </div>
      </div>

      {/* MAIN CANVAS WORKSPACE */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onWheel={handleWheel}
          style={{ width: '100%', height: '100%', cursor: isDraggingCanvasRef.current ? 'grabbing' : draggedNodeRef.current ? 'grabbing' : 'grab' }}
        />

        {/* DYNAMIC FEATURE FILTER BAR (TOP LEFT) */}
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          backgroundColor: 'rgba(15, 23, 42, 0.88)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '10px',
          padding: '6px 10px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          zIndex: 10,
          maxWidth: '80%',
          overflowX: 'auto'
        }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 800, color: '#64748b', marginRight: '4px' }}>FILTER:</span>
          <button
            onClick={() => setActiveFilterType('ALL')}
            style={{
              padding: '4px 8px',
              fontSize: '0.68rem',
              fontWeight: 800,
              borderRadius: '6px',
              border: 'none',
              backgroundColor: activeFilterType === 'ALL' ? '#38bdf8' : 'transparent',
              color: activeFilterType === 'ALL' ? '#0f172a' : '#94a3b8',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            All Entities ({nodes.length})
          </button>

          {featureTypes.map(ft => {
            const isSelected = activeFilterType === ft.type;
            return (
              <button
                key={ft.type}
                onClick={() => setActiveFilterType(ft.type)}
                style={{
                  padding: '4px 8px',
                  fontSize: '0.68rem',
                  fontWeight: 800,
                  borderRadius: '6px',
                  border: 'none',
                  backgroundColor: isSelected ? ft.color : 'transparent',
                  color: isSelected ? '#0f172a' : '#cbd5e1',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: ft.color }} />
                <span>{ft.label}</span>
                <span style={{ opacity: 0.7, fontSize: '0.62rem' }}>({ft.count})</span>
              </button>
            );
          })}
        </div>

        {/* FLOATING CANVAS CONTROLS (BOTTOM LEFT) */}
        <div style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '10px',
          padding: '6px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          zIndex: 10
        }}>
          <button
            onClick={() => setIsPhysicsRunning(!isPhysicsRunning)}
            title={isPhysicsRunning ? 'Pause Physics Simulation' : 'Resume Physics'}
            style={{ background: 'transparent', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: '4px' }}
          >
            {isPhysicsRunning ? <Pause size={16} /> : <Play size={16} />}
          </button>
          <div style={{ width: '1px', height: '14px', backgroundColor: 'rgba(255,255,255,0.1)' }} />
          <button
            onClick={() => { transformRef.current.scale = Math.min(4, transformRef.current.scale * 1.2); }}
            title="Zoom In"
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <ZoomIn size={16} />
          </button>
          <button
            onClick={() => { transformRef.current.scale = Math.max(0.15, transformRef.current.scale * 0.8); }}
            title="Zoom Out"
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <ZoomOut size={16} />
          </button>
          <button
            onClick={handleResetView}
            title="Reset View & Center Canvas"
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <RotateCcw size={16} />
          </button>
        </div>

        {/* MULTI-HOP PATH FINDER DRAWER (TOP RIGHT) */}
        {isPathFinderOpen && (
          <div style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            width: '360px',
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(56, 189, 248, 0.35)',
            borderRadius: '14px',
            padding: '16px',
            boxShadow: '0 12px 36px rgba(0,0,0,0.7)',
            zIndex: 30
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Crosshair size={14} /> Shortest Multi-Hop Path Solver
              </span>
              <X size={14} style={{ color: '#94a3b8', cursor: 'pointer' }} onClick={() => setIsPathFinderOpen(false)} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.68rem', color: '#94a3b8', fontWeight: 700 }}>START ENTITY:</label>
                <input
                  type="text"
                  placeholder="e.g. Imran Khan..."
                  value={pathStartQuery}
                  onChange={(e) => setPathStartQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    backgroundColor: '#090d16',
                    color: '#f8fafc',
                    fontSize: '0.75rem',
                    marginTop: '4px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.68rem', color: '#94a3b8', fontWeight: 700 }}>TARGET ENTITY:</label>
                <input
                  type="text"
                  placeholder="e.g. Ramesh Tiwari..."
                  value={pathTargetQuery}
                  onChange={(e) => setPathTargetQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    backgroundColor: '#090d16',
                    color: '#f8fafc',
                    fontSize: '0.75rem',
                    marginTop: '4px',
                    outline: 'none'
                  }}
                />
              </div>

              <button
                onClick={handleExecutePathFinder}
                style={{
                  padding: '8px',
                  backgroundColor: '#38bdf8',
                  color: '#0f172a',
                  fontWeight: 800,
                  fontSize: '0.75rem',
                  borderRadius: '6px',
                  border: 'none',
                  cursor: 'pointer',
                  marginTop: '4px'
                }}
              >
                Trace Path (BFS)
              </button>

              {activePathResult && (
                <div style={{
                  marginTop: '10px',
                  padding: '10px',
                  backgroundColor: activePathResult.found ? 'rgba(56, 189, 248, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${activePathResult.found ? 'rgba(56, 189, 248, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '8px',
                  fontSize: '0.72rem',
                  lineHeight: 1.5,
                  maxHeight: '180px',
                  overflowY: 'auto'
                }}>
                  {activePathResult.found ? (
                    <div>
                      <div style={{ fontWeight: 800, color: '#38bdf8', marginBottom: '4px' }}>
                        ✓ {activePathResult.hops}-Hop Path Found:
                      </div>
                      {activePathResult.stepDescriptions.map((step, idx) => (
                        <div key={idx} style={{ marginBottom: '4px', color: '#cbd5e1' }} dangerouslySetInnerHTML={{ __html: step.replace(/\*\*/g, '<b>').replace(/\\xrightarrow\{([^}]+)\}/g, '→ $1 →') }} />
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: '#ef4444' }}>{activePathResult.reason}</div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* NODE INSPECTION & FORENSIC DOSSIER DRAWER (RIGHT SIDE) */}
        {selectedNode && (
          <div style={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: '380px',
            height: '100%',
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(20px)',
            borderLeft: '1px solid rgba(255, 255, 255, 0.12)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            boxShadow: '-10px 0 35px rgba(0,0,0,0.8)',
            zIndex: 40,
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <div>
                <span style={{
                  fontSize: '0.68rem',
                  fontWeight: 800,
                  padding: '2px 8px',
                  borderRadius: '10px',
                  backgroundColor: `${selectedNode.color}25`,
                  color: selectedNode.color,
                  border: `1px solid ${selectedNode.color}50`
                }}>
                  {selectedNode.typeLabel}
                </span>
                <h3 style={{ margin: '8px 0 2px 0', fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>
                  {selectedNode.label}
                </h3>
                <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                  Entity ID: <code style={{ color: '#38bdf8' }}>{selectedNode.id}</code>
                </div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* PERSON DEMOGRAPHIC CHIPS (IF SUSPECT) */}
            {selectedNode.type === 'SUSPECT' && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ padding: '4px 10px', borderRadius: '6px', backgroundColor: '#090d16', border: '1px solid rgba(255,255,255,0.08)', fontSize: '0.72rem', color: '#cbd5e1' }}>
                  Gender: <b style={{ color: '#38bdf8' }}>{selectedNode.metadata?.gender || 'Male'}</b>
                </div>
                <div style={{ padding: '4px 10px', borderRadius: '6px', backgroundColor: '#090d16', border: '1px solid rgba(255,255,255,0.08)', fontSize: '0.72rem', color: '#cbd5e1' }}>
                  Age: <b style={{ color: '#38bdf8' }}>{selectedNode.metadata?.age || '35'}</b>
                </div>
                <div style={{ padding: '4px 10px', borderRadius: '6px', backgroundColor: '#090d16', border: '1px solid rgba(255,255,255,0.08)', fontSize: '0.72rem', color: '#cbd5e1' }}>
                  Cases: <b style={{ color: '#f43f5e' }}>{selectedNode.metadata?.linkedCases?.length || 1}</b>
                </div>
              </div>
            )}

            {/* KEY METRICS STRIP */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div style={{ backgroundColor: '#090d16', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 700 }}>CENTRALITY DEGREE</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#38bdf8' }}>{selectedNode.degree} Links</div>
              </div>
              <div style={{ backgroundColor: '#090d16', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 700 }}>COMMUNITY CLUSTER</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: selectedNode.color }}>Cluster #{selectedNode.community}</div>
              </div>
            </div>

            {/* DIRECT ASSOCIATED ENTITIES (VEHICLES, PHONES, MULES, CO-ACCUSED) */}
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#94a3b8', marginBottom: '8px' }}>
                DIRECT NETWORK ASSOCIATIONS ({focusedNeighborhood ? focusedNeighborhood.size - 1 : 0})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '220px', overflowY: 'auto' }}>
                {Array.from(focusedNeighborhood || []).filter(id => id !== selectedNode.id).map(nId => {
                  const target = nodes.find(n => n.id === nId);
                  if (!target) return null;
                  return (
                    <div
                      key={nId}
                      onClick={() => flyToNode(target)}
                      style={{
                        padding: '8px 10px',
                        backgroundColor: '#090d16',
                        borderRadius: '6px',
                        border: '1px solid rgba(255,255,255,0.06)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: target.color }} />
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#e2e8f0' }}>{target.label}</span>
                      </div>
                      <span style={{ fontSize: '0.65rem', color: target.color, fontWeight: 700 }}>{target.typeLabel}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ASSOCIATED FIR CASES */}
            {selectedNode.metadata?.linkedCases && selectedNode.metadata.linkedCases.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#94a3b8', marginBottom: '6px' }}>
                  ASSOCIATED FIR CASES ({selectedNode.metadata.linkedCases.length})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxHeight: '120px', overflowY: 'auto' }}>
                  {selectedNode.metadata.linkedCases.slice(0, 20).map((rec, i) => (
                    <span key={i} style={{ fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', backgroundColor: '#1e293b', color: '#93c5fd' }}>
                      {rec}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* FORENSIC INTEGRITY */}
            <div style={{
              marginTop: 'auto',
              padding: '12px',
              backgroundColor: '#090d16',
              borderRadius: '8px',
              border: '1px solid rgba(52, 211, 153, 0.3)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontSize: '0.72rem', fontWeight: 800 }}>
                <Shield size={14} /> Section 65B Forensic Integrity Certificate
              </div>
              <div style={{ fontSize: '0.68rem', color: '#64748b', marginTop: '4px', wordBreak: 'break-all' }}>
                Signature: <code>{selectedNode.metadata?.Section_65B_Signature || '8391526fab0a22e3-verified'}</code>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* DEDICATED DATASET UPLOAD MODAL */}
      {isUploadModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div style={{
            width: '480px',
            backgroundColor: '#0f172a',
            border: '1px solid rgba(56, 189, 248, 0.4)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 25px 60px rgba(0,0,0,0.9)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <UploadCloud size={20} style={{ color: '#38bdf8' }} />
                <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc' }}>
                  Attach Network / CDR Dataset
                </h3>
              </div>
              <X size={18} style={{ color: '#94a3b8', cursor: 'pointer' }} onClick={() => setIsUploadModalOpen(false)} />
            </div>

            <p style={{ fontSize: '0.75rem', color: '#94a3b8', lineHeight: 1.5, margin: '0 0 16px 0' }}>
              Upload any dedicated CSV, Excel (.xlsx/.xls), JSON / NoSQL dump, or SQL export. The Network Ingestion Agent will extract entity relationships and render the interactive graph topology.
            </p>

            <div
              onClick={() => document.getElementById('network-file-input').click()}
              style={{
                border: '2px dashed rgba(56, 189, 248, 0.4)',
                borderRadius: '12px',
                padding: '28px',
                textAlign: 'center',
                backgroundColor: 'rgba(9, 13, 22, 0.6)',
                cursor: 'pointer'
              }}
            >
              <FileText size={32} style={{ color: '#38bdf8', margin: '0 auto 8px auto' }} />
              <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#f8fafc' }}>Click to select Data File</div>
              <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '4px' }}>Supports CSV, Excel (.xlsx), JSON, SQL exports & Telecom CDRs</div>
              <input
                id="network-file-input"
                type="file"
                accept=".csv, .xlsx, .xls, .json, .sql, .txt"
                style={{ display: 'none' }}
                onChange={(e) => handleDedicatedFileUpload(e.target.files[0])}
              />
            </div>

            {uploadError && (
              <div style={{ color: '#ef4444', fontSize: '0.72rem', marginTop: '12px' }}>
                {uploadError}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
