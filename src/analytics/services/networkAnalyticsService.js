/**
 * KSP Sentinel AI — Dynamic Entity Link Analytics & Graph Intelligence Service
 * 
 * SOLID ARCHITECTURE:
 * - Real Investigative Entities (Suspects, Vehicles, Phones, Mule Accounts, Police Stations, Operations)
 * - Demographic & Case Properties (Gender, Age, Status, Dates, Amounts) attached to Node & Edge Metadata
 * - Pure Multi-Hop Relational Linkage (Shared Vehicles, Shared Phones, Co-Accused)
 * - $O(V+E)$ BFS Path Solver for the Chatbot Agent
 */

// Graphify Chromatic Palette for Entity Types
export const GRAPHIFY_COLOR_PALETTE = {
  SUSPECT: '#f43f5e',         // Crimson Rose (Primary Suspects & Co-Accused)
  VEHICLE: '#0284c7',         // Ocean Blue (Getaway Transport)
  PHONE: '#a855f7',           // Electric Purple (Burner Phones & Devices)
  FINANCIAL: '#10b981',       // Emerald Green (Bank Accounts & Mule UPIs)
  POLICE_STATION: '#f59e0b',  // Amber Gold (Police Stations & Precincts)
  OPERATION: '#06b6d4'        // Cyan (Syndicate Operation Rings)
};

// ==========================================
// 1. STATISTICAL ENTITY PROFILER & CLASSIFIER
// ==========================================

export class StatisticalColumnProfiler {
  /**
   * Intelligently categorizes columns into:
   * 1. INVESTIGATIVE_ENTITIES (Suspects, Vehicles, Phones, Mules, Stations, Operations) -> Graph Nodes
   * 2. DEMOGRAPHIC_PROPERTIES (Gender, Age) -> Node Metadata
   * 3. CASE_TRANSACTION_PROPERTIES (FIR Number, Status, Amounts, Dates, Signatures) -> Edge & Context Metadata
   */
  static profileDataset(records, headers) {
    if (!records || records.length === 0 || !headers || headers.length === 0) {
      return { entityConfigs: [], transactionKey: null };
    }

    const sample = records.slice(0, Math.min(records.length, 300));
    const entityConfigs = [];

    // Semantic Regex Profiler for Investigative Entities
    const entityPatterns = [
      {
        type: 'SUSPECT',
        typeLabel: 'Suspect / Accused',
        color: GRAPHIFY_COLOR_PALETTE.SUSPECT,
        regex: /(suspect_name|accused_name|suspect|perpetrator|person_name)/i
      },
      {
        type: 'SUSPECT',
        typeLabel: 'Co-Accused / Associate',
        color: GRAPHIFY_COLOR_PALETTE.SUSPECT,
        regex: /(co_accused|associate|accomplice)/i
      },
      {
        type: 'VEHICLE',
        typeLabel: 'Vehicle / Transport',
        color: GRAPHIFY_COLOR_PALETTE.VEHICLE,
        regex: /(vehicle_number|vehicle|veh_no|reg_no|license_plate|getaway_car)/i
      },
      {
        type: 'PHONE',
        typeLabel: 'Phone / Burner Device',
        color: GRAPHIFY_COLOR_PALETTE.PHONE,
        regex: /(caller_phone_number|phone_number|phone|mobile|caller|msisdn|imei)/i
      },
      {
        type: 'FINANCIAL',
        typeLabel: 'Bank / Mule UPI Account',
        color: GRAPHIFY_COLOR_PALETTE.FINANCIAL,
        regex: /(mule_bank_upi_account|bank_account|upi_id|mule_account|wallet_address|crypto_wallet)/i
      },
      {
        type: 'POLICE_STATION',
        typeLabel: 'Police Station / Location',
        color: GRAPHIFY_COLOR_PALETTE.POLICE_STATION,
        regex: /(police_station|ps_name|station_name|jurisdiction)/i
      },
      {
        type: 'OPERATION',
        typeLabel: 'Crime Syndicate / Operation',
        color: GRAPHIFY_COLOR_PALETTE.OPERATION,
        regex: /(crime_category|subcategory|operation_name|syndicate|motive)/i
      }
    ];

    // Find columns matching primary investigative entity roles
    headers.forEach(header => {
      // Exclude demographic properties, dates, continuous floats, or status columns from becoming nodes
      const isDemographicOrMetric = /gender|age|status|date|year|month|amount|loss|recovered|percentage|days|latitude|longitude|lat|lng|signature|sha256/i.test(header);
      
      if (!isDemographicOrMetric) {
        for (const ep of entityPatterns) {
          if (ep.regex.test(header)) {
            // Ensure column has valid values
            const hasValues = sample.some(r => r[header] && String(r[header]).trim() !== '' && String(r[header]).trim() !== 'None');
            if (hasValues && !entityConfigs.some(ec => ec.header === header)) {
              entityConfigs.push({
                header,
                type: ep.type,
                typeLabel: ep.typeLabel,
                color: ep.color
              });
            }
            break;
          }
        }
      }
    });

    // Fallback: If no regex matched, dynamically pick categorical columns with repeating entities
    if (entityConfigs.length === 0) {
      headers.forEach(header => {
        const isExcluded = /gender|age|status|date|year|month|amount|loss|recovered|percentage|days|latitude|longitude|signature|sha256/i.test(header);
        if (!isExcluded) {
          const values = sample.map(r => String(r[header] || '').trim()).filter(v => v && v !== 'None');
          const uniqueCount = new Set(values).size;
          if (uniqueCount >= 2 && uniqueCount <= sample.length * 0.5) {
            entityConfigs.push({
              header,
              type: 'ENTITY',
              typeLabel: header.replace(/_/g, ' '),
              color: '#38bdf8'
            });
          }
        }
      });
    }

    const transactionCol = headers.find(h => /fir_number|fir_no|case_id|crime_id|record_id/i.test(h)) || headers[0];

    return {
      entityConfigs,
      transactionKey: transactionCol
    };
  }
}

// ==========================================
// 2. MULTI-HOP GRAPH TOPOLOGY BUILDER
// ==========================================

export class GraphTopologyBuilder {
  /**
   * Builds high-fidelity, uncluttered multi-hop investigative entity network.
   * Connects Suspects to Co-Accused, Getaway Vehicles, Burner Phones,
   * Bank Mule Accounts, Police Stations, and Crime Syndicates.
   */
  static buildTopology(records, headers) {
    if (!records || records.length === 0 || !headers || headers.length === 0) {
      return {
        nodes: [],
        edges: [],
        nodeCount: 0,
        edgeCount: 0,
        featureTypes: [],
        communitiesCount: 0,
        godNodes: [],
        builtAt: new Date().toISOString()
      };
    }

    const { entityConfigs, transactionKey } = StatisticalColumnProfiler.profileDataset(records, headers);

    const nodesMap = new Map();
    const edgesList = [];
    const edgeSet = new Set();
    const typeCountMap = new Map();

    const addNode = (id, label, type, typeLabel, color, metadata = {}) => {
      const cleanId = String(id).trim();
      if (!cleanId || cleanId === 'undefined' || cleanId === 'null' || cleanId === 'None' || cleanId === '0' || cleanId === '') {
        return null;
      }

      const nodeKey = `${type}:::${cleanId}`;

      if (!nodesMap.has(nodeKey)) {
        typeCountMap.set(type, (typeCountMap.get(type) || 0) + 1);

        nodesMap.set(nodeKey, {
          id: nodeKey,
          rawId: cleanId,
          label: String(label).trim(),
          type,
          typeLabel,
          color,
          degree: 0,
          inDegree: 0,
          outDegree: 0,
          community: 0,
          metadata: {
            ...metadata,
            linkedCases: [],
            totalLossINR: 0,
            associatedStations: new Set()
          },
          x: 0,
          y: 0,
          vx: 0,
          vy: 0
        });
      }

      const node = nodesMap.get(nodeKey);
      
      // Accumulate metadata across cases
      if (metadata.caseId && !node.metadata.linkedCases.includes(metadata.caseId)) {
        node.metadata.linkedCases.push(metadata.caseId);
      }
      if (metadata.lossINR) {
        node.metadata.totalLossINR += Number(metadata.lossINR) || 0;
      }
      if (metadata.policeStation) {
        node.metadata.associatedStations.add(metadata.policeStation);
      }
      if (metadata.gender) node.metadata.gender = metadata.gender;
      if (metadata.age) node.metadata.age = metadata.age;

      return node;
    };

    const addEdge = (sourceKey, targetKey, relation, weight = 1.0, caseRef = '') => {
      if (!sourceKey || !targetKey || sourceKey === targetKey) return;
      const key1 = `${sourceKey}__${targetKey}`;
      const key2 = `${targetKey}__${sourceKey}`;
      if (edgeSet.has(key1) || edgeSet.has(key2)) return;

      edgeSet.add(key1);
      edgesList.push({
        source: sourceKey,
        target: targetKey,
        relation,
        weight,
        caseRef
      });

      const sNode = nodesMap.get(sourceKey);
      const tNode = nodesMap.get(targetKey);
      if (sNode) sNode.degree = (sNode.degree || 0) + 1;
      if (tNode) tNode.degree = (tNode.degree || 0) + 1;
    };

    // Parse each record into meaningful criminal entity relationships
    records.forEach((row, rowIdx) => {
      const caseId = transactionKey && row[transactionKey] ? String(row[transactionKey]) : `FIR-${rowIdx + 1}`;
      const lossINR = row.Loss_Amount_INR || row.loss || row.amount || 0;
      const gender = row.Accused_Gender || row.gender || 'Unknown';
      const age = row.Accused_Age || row.age || 35;
      const station = row.Police_Station || row.station || '';

      const baseMeta = { caseId, lossINR, gender, age, policeStation: station };

      // 1. Primary Suspect
      const suspectCol = entityConfigs.find(ec => ec.type === 'SUSPECT' && !/co_accused/i.test(ec.header));
      let primarySuspectNode = null;

      if (suspectCol && row[suspectCol.header]) {
        const val = String(row[suspectCol.header]).trim();
        if (val && val !== 'None') {
          primarySuspectNode = addNode(val, val, 'SUSPECT', 'Suspect / Accused', suspectCol.color, baseMeta);
        }
      }

      // 2. Co-Accused Suspect
      const coCol = entityConfigs.find(ec => /co_accused|associate/i.test(ec.header));
      if (coCol && row[coCol.header]) {
        const coVal = String(row[coCol.header]).trim();
        if (coVal && coVal !== 'None') {
          const coNode = addNode(coVal, coVal, 'SUSPECT', 'Co-Accused', coCol.color, baseMeta);
          if (coNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, coNode.id, 'CO_ACCUSED', 2.0, caseId);
          }
        }
      }

      // 3. Vehicles
      const vehCol = entityConfigs.find(ec => ec.type === 'VEHICLE');
      if (vehCol && row[vehCol.header]) {
        const val = String(row[vehCol.header]).trim();
        if (val && val !== 'None') {
          const vNode = addNode(val, val, 'VEHICLE', 'Getaway Vehicle', vehCol.color, baseMeta);
          if (vNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, vNode.id, 'OPERATES_VEHICLE', 1.5, caseId);
          }
        }
      }

      // 4. Burner Phones
      const phoneCol = entityConfigs.find(ec => ec.type === 'PHONE');
      if (phoneCol && row[phoneCol.header]) {
        const val = String(row[phoneCol.header]).trim();
        if (val && val !== 'None' && val !== '+91-99000-00000') {
          const phNode = addNode(val, val, 'PHONE', 'Burner Device', phoneCol.color, baseMeta);
          if (phNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, phNode.id, 'CALLER_DEVICE', 1.3, caseId);
          }
        }
      }

      // 5. Mule Bank / UPI Accounts
      const finCol = entityConfigs.find(ec => ec.type === 'FINANCIAL');
      if (finCol && row[finCol.header]) {
        const val = String(row[finCol.header]).trim();
        if (val && val !== 'None' && !val.includes('unassigned')) {
          const fNode = addNode(val, val, 'FINANCIAL', 'Bank / UPI Mule', finCol.color, baseMeta);
          if (fNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, fNode.id, 'TRANSFERS_TO_MULE', 1.6, caseId);
          }
        }
      }

      // 6. Police Stations
      const psCol = entityConfigs.find(ec => ec.type === 'POLICE_STATION');
      if (psCol && row[psCol.header]) {
        const val = String(row[psCol.header]).trim();
        if (val && val !== 'None') {
          const psNode = addNode(val, val, 'POLICE_STATION', 'Police Station', psCol.color, baseMeta);
          if (psNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, psNode.id, 'BOOKED_AT', 1.0, caseId);
          }
        }
      }

      // 7. Syndicate Operation Rings
      const opCol = entityConfigs.find(ec => ec.type === 'OPERATION');
      if (opCol && row[opCol.header]) {
        const val = String(row[opCol.header]).trim();
        if (val && val !== 'None') {
          const opNode = addNode(val, val, 'OPERATION', 'Syndicate Ring', opCol.color, baseMeta);
          if (opNode && primarySuspectNode) {
            addEdge(primarySuspectNode.id, opNode.id, 'OPERATES_IN', 1.4, caseId);
          }
        }
      }
    });

    const nodes = Array.from(nodesMap.values());
    nodes.sort((a, b) => (b.degree || 0) - (a.degree || 0));

    // Community Detection (Modularity by type & high-centrality hubs)
    const communityMap = new Map();
    let communityIdx = 0;
    nodes.forEach(n => {
      const groupKey = n.type;
      if (!communityMap.has(groupKey)) {
        communityMap.set(groupKey, ++communityIdx);
      }
      n.community = communityMap.get(groupKey);
    });

    // Graphify Radial Concentric Orbit Layout (Wide Spacing centered at 0, 0)
    const totalNodes = nodes.length || 1;
    nodes.forEach((n, idx) => {
      let baseRadius = 240;
      if (n.type === 'SUSPECT') {
        baseRadius = 180 + (idx % 6) * 35; // Core suspect inner orbit
      } else if (n.type === 'OPERATION') {
        baseRadius = 280 + (idx % 4) * 30; // Syndicate ring orbit
      } else if (n.type === 'VEHICLE' || n.type === 'PHONE') {
        baseRadius = 380 + (idx % 8) * 35; // Asset mid orbit
      } else {
        baseRadius = 490 + (idx % 10) * 40; // Stations & Mules outer orbit
      }

      const angle = (idx / totalNodes) * Math.PI * 2 + (n.community * 0.9);
      n.x = baseRadius * Math.cos(angle);
      n.y = baseRadius * Math.sin(angle);
      n.vx = 0;
      n.vy = 0;
    });

    // Dynamic Feature Types list
    const featureTypes = Array.from(new Set(nodes.map(n => n.type))).map(type => {
      const sampleNode = nodes.find(n => n.type === type);
      return {
        type,
        label: sampleNode?.typeLabel || type,
        color: sampleNode?.color || '#38bdf8',
        count: typeCountMap.get(type) || 0
      };
    });

    return {
      nodes,
      edges: edgesList,
      nodeCount: nodes.length,
      edgeCount: edgesList.length,
      featureTypes,
      communitiesCount: communityMap.size,
      godNodes: nodes.slice(0, 8),
      builtAt: new Date().toISOString()
    };
  }
}

// ==========================================
// 3. DETERMINISTIC SHORTEST-PATH & DOSSIER SOLVER (BFS)
// ==========================================

export class GraphPathSolver {
  static findShortestPath(nodes, edges, startQuery, targetQuery) {
    if (!nodes || nodes.length === 0 || !edges || edges.length === 0) {
      return { found: false, reason: 'Graph contains no nodes or edges.' };
    }

    const qA = String(startQuery).trim().toLowerCase();
    const qB = String(targetQuery).trim().toLowerCase();

    const startNode = nodes.find(n => n.label.toLowerCase() === qA || n.rawId?.toLowerCase() === qA || n.id.toLowerCase().includes(qA));
    const targetNode = nodes.find(n => n.label.toLowerCase() === qB || n.rawId?.toLowerCase() === qB || n.id.toLowerCase().includes(qB));

    if (!startNode) return { found: false, reason: `Entity '${startQuery}' not found in active graph.` };
    if (!targetNode) return { found: false, reason: `Target entity '${targetQuery}' not found in active graph.` };
    if (startNode.id === targetNode.id) {
      return {
        found: true,
        hops: 0,
        pathNodes: [startNode],
        pathEdges: [],
        stepDescriptions: [`Start and Target are the same entity: **${startNode.label}** (${startNode.typeLabel}).`],
        narrative: `Start and Target are the same entity: **${startNode.label}** (${startNode.typeLabel}).`
      };
    }

    const adj = new Map();
    nodes.forEach(n => adj.set(n.id, []));
    edges.forEach(e => {
      const s = typeof e.source === 'object' ? e.source.id : e.source;
      const t = typeof e.target === 'object' ? e.target.id : e.target;
      if (adj.has(s) && adj.has(t)) {
        adj.get(s).push({ neighbor: t, edge: e });
        adj.get(t).push({ neighbor: s, edge: e });
      }
    });

    const queue = [[startNode.id]];
    const visited = new Set([startNode.id]);
    const edgeTrail = new Map();
    let foundPath = null;

    while (queue.length > 0) {
      const path = queue.shift();
      const currentId = path[path.length - 1];

      if (currentId === targetNode.id) {
        foundPath = path;
        break;
      }

      const neighbors = adj.get(currentId) || [];
      for (const { neighbor, edge } of neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          edgeTrail.set(`${currentId}->${neighbor}`, edge);
          queue.push([...path, neighbor]);
        }
      }
    }

    if (!foundPath) {
      return {
        found: false,
        reason: `No direct or multi-hop link exists between '${startNode.label}' and '${targetNode.label}'.`,
        startNode,
        targetNode
      };
    }

    const pathNodes = foundPath.map(id => nodes.find(n => n.id === id));
    const pathEdges = [];
    const stepDescriptions = [];

    for (let i = 0; i < foundPath.length - 1; i++) {
      const fromId = foundPath[i];
      const toId = foundPath[i + 1];
      const edge = edgeTrail.get(`${fromId}->${toId}`) || edgeTrail.get(`${toId}->${fromId}`) || { relation: 'LINKED' };
      pathEdges.push({ from: fromId, to: toId, edge });

      const fromNode = nodes.find(n => n.id === fromId);
      const toNode = nodes.find(n => n.id === toId);

      const stepText = `**Step ${i + 1}:** [${fromNode.typeLabel}] \`${fromNode.label}\` $\\xrightarrow{\\text{${edge.relation || 'LINKED'}}}$ [${toNode.typeLabel}] \`${toNode.label}\`${edge.caseRef ? ` *(Case: ${edge.caseRef})*` : ''}`;
      stepDescriptions.push(stepText);
    }

    const narrative = `### 🕸️ Multi-Hop Link Verification (${pathNodes.length - 1} Hops):\n\n` +
      `**Causal Route from \`${startNode.label}\` to \`${targetNode.label}\`:**\n\n` +
      stepDescriptions.join('\n\n') +
      `\n\n🛡️ *Sec 65B Audit: Path deterministically resolved across ${pathNodes.length} graph entities.*`;

    return {
      found: true,
      hops: pathNodes.length - 1,
      pathNodes,
      pathEdges,
      stepDescriptions,
      narrative,
      startNode,
      targetNode
    };
  }

  static getEntityDossier(nodes, edges, entityQuery) {
    const q = String(entityQuery).trim().toLowerCase();
    const node = nodes.find(n => n.label.toLowerCase() === q || n.rawId?.toLowerCase() === q || n.id.toLowerCase().includes(q));
    if (!node) return { found: false, reason: `Entity '${entityQuery}' not found.` };

    const directNeighbors = [];
    edges.forEach(e => {
      const s = typeof e.source === 'object' ? e.source.id : e.source;
      const t = typeof e.target === 'object' ? e.target.id : e.target;
      if (s === node.id) {
        const targetObj = nodes.find(n => n.id === t);
        if (targetObj) directNeighbors.push({ node: targetObj, relation: e.relation });
      } else if (t === node.id) {
        const sourceObj = nodes.find(n => n.id === s);
        if (sourceObj) directNeighbors.push({ node: sourceObj, relation: e.relation });
      }
    });

    return {
      found: true,
      node,
      directConnectionsCount: directNeighbors.length,
      directNeighbors,
      linkedCases: node.metadata?.linkedCases || []
    };
  }
}

// ==========================================
// 4. GLOBAL NETWORK TOPOLOGY STORE (SINGLETON)
// ==========================================

class NetworkTopologyStore {
  constructor() {
    this.state = {
      isLocked: false,
      datasetName: '',
      nodes: [],
      edges: [],
      featureTypes: [],
      godNodes: [],
      selectedNode: null,
      activePath: null,
      lastUpdated: null
    };
    this.listeners = new Set();
  }

  getState() {
    return this.state;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    this.listeners.forEach(l => l(this.state));
  }

  loadDataset(records, headers, datasetName = 'Active Investigation Dataset') {
    if (!records || records.length === 0 || !headers || headers.length === 0) {
      return;
    }

    const { nodes, edges, featureTypes, godNodes } = GraphTopologyBuilder.buildTopology(records, headers);

    this.state = {
      ...this.state,
      isLocked: nodes.length > 0,
      datasetName,
      nodes,
      edges,
      featureTypes,
      godNodes,
      selectedNode: null,
      activePath: null,
      lastUpdated: new Date().toISOString()
    };

    this.notify();
  }

  loadDedicatedNetworkData(records, headers, datasetName = 'Dedicated Network Dump') {
    this.loadDataset(records, headers, datasetName);
  }

  reset() {
    this.state = {
      isLocked: false,
      datasetName: '',
      nodes: [],
      edges: [],
      featureTypes: [],
      godNodes: [],
      selectedNode: null,
      activePath: null,
      lastUpdated: null
    };
    this.notify();
  }
}

export const globalNetworkStore = new NetworkTopologyStore();

// ==========================================
// 5. AUTONOMOUS GRAPH QUERY TOOL AGENT (CHATBOT INTERFACE)
// ==========================================

export class GraphQueryToolAgent {
  static get_graph_status() {
    const state = globalNetworkStore.getState();
    return {
      is_locked: state.isLocked,
      dataset_name: state.datasetName,
      total_nodes: state.nodes.length,
      total_edges: state.edges.length,
      feature_types: state.featureTypes.map(f => f.label),
      top_hubs: state.godNodes.map(g => `${g.label} (${g.typeLabel}, ${g.degree} links)`)
    };
  }

  static trace_shortest_path(startEntity, targetEntity) {
    const state = globalNetworkStore.getState();
    if (!state.isLocked || state.nodes.length === 0) {
      return {
        found: false,
        reason: "No active relational graph dataset is locked in the platform.",
        suggestion: "Please attach a dataset or open the Network Link Intelligence view."
      };
    }

    return GraphPathSolver.findShortestPath(state.nodes, state.edges, startEntity, targetEntity);
  }

  static get_entity_dossier(entityQuery) {
    const state = globalNetworkStore.getState();
    if (!state.isLocked) {
      return { found: false, reason: "No active network dataset is locked." };
    }
    return GraphPathSolver.getEntityDossier(state.nodes, state.edges, entityQuery);
  }

  static find_syndicate_hubs(topN = 5) {
    const state = globalNetworkStore.getState();
    if (!state.isLocked) return { hubs: [] };
    return {
      hubs: state.godNodes.slice(0, topN).map(n => ({
        id: n.id,
        label: n.label,
        type: n.typeLabel,
        connections: n.degree,
        metadata: n.metadata
      }))
    };
  }
}
