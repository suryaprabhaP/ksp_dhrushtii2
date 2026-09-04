import React, { useEffect } from 'react';
import {
  SlidersHorizontal,
  FileText,
  ChevronRight,
  ChevronLeft,
  Flame,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Layers,
  Eye,
  EyeOff,
  Filter
} from 'lucide-react';

/**
 * SpatialRightDeck — Unified Floating Right Command & Intelligence Deck in DRISHTI Warm Parchment Theme (SOLID: SRP + ISP)
 * Features dual-mode tab switching:
 * - Tab 1: Control Deck (Slicers, Layer Toggles, Live Incident KPIs)
 * - Tab 2: Intelligence Dossier (Deep-Dive Analysis, Threat Level, AI Leads)
 */
export default function SpatialRightDeck({
  isCollapsed,
  onToggleCollapse,
  activeTab,
  onTabChange,
  // Slicers
  dynamicFilters,
  selectedCategory,
  onCategoryChange,
  selectedDivision,
  onDivisionChange,
  selectedStation,
  onStationChange,
  selectedStatus,
  onStatusChange,
  // Layer Toggles
  showStateBoundary,
  onToggleStateBoundary,
  showDistricts,
  onToggleDistricts,
  showDistrictLabels,
  onToggleDistrictLabels,
  // Metrics
  kpiSummary,
  selectedHotspot,
  onClearHotspot,
  selectedDistrictName,
  onClearDistrict,
  onBackToChat,
  onStartInvestigation
}) {
  // Auto-switch to Dossier tab when a hotspot or district is clicked
  useEffect(() => {
    if (selectedHotspot || selectedDistrictName) {
      onTabChange('DOSSIER');
    }
  }, [selectedHotspot, selectedDistrictName, onTabChange]);

  return (
    <aside style={{
      position: 'absolute',
      top: '16px',
      right: '16px',
      width: isCollapsed ? '42px' : '340px',
      maxHeight: 'calc(100% - 32px)',
      backgroundColor: '#FCFCFA',
      border: '1px solid #D4CEBF',
      borderRadius: '14px',
      zIndex: 999,
      boxShadow: '0 12px 30px rgba(19, 43, 32, 0.08)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      transition: 'width 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
      pointerEvents: 'auto',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    }}>
      {/* Deck Header & Collapse Toggle */}
      <div style={{
        padding: isCollapsed ? '12px 0' : '8px 12px',
        borderBottom: '1px solid #D4CEBF',
        display: 'flex',
        alignItems: 'center',
        justifyContent: isCollapsed ? 'center' : 'space-between',
        backgroundColor: '#FCFCFA'
      }}>
        {!isCollapsed && (
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              onClick={() => onTabChange('CONTROLS')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '5px 10px',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.72rem',
                fontWeight: 800,
                cursor: 'pointer',
                backgroundColor: activeTab === 'CONTROLS' ? '#EFEBE2' : 'transparent',
                color: activeTab === 'CONTROLS' ? '#132B20' : '#6B7A72',
                borderBottom: activeTab === 'CONTROLS' ? '2px solid #D49B44' : '2px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              <SlidersHorizontal size={12} color={activeTab === 'CONTROLS' ? '#132B20' : '#6B7A72'} />
              <span>Controls</span>
            </button>

            <button
              onClick={() => onTabChange('DOSSIER')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '5px 10px',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.72rem',
                fontWeight: 800,
                cursor: 'pointer',
                backgroundColor: activeTab === 'DOSSIER' ? '#EFEBE2' : 'transparent',
                color: activeTab === 'DOSSIER' ? '#132B20' : '#6B7A72',
                borderBottom: activeTab === 'DOSSIER' ? '2px solid #D49B44' : '2px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              <FileText size={12} color={activeTab === 'DOSSIER' ? '#132B20' : '#6B7A72'} />
              <span>Dossier</span>
              {(selectedHotspot || selectedDistrictName) && (
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: '#DC2626',
                  boxShadow: '0 0 4px #DC2626'
                }} />
              )}
            </button>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#6B7A72',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '6px',
            transition: 'color 0.15s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#132B20'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7A72'}
          title={isCollapsed ? 'Expand Command Deck' : 'Collapse Command Deck'}
        >
          {isCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      {/* Main Content Body (Scrollable) */}
      {!isCollapsed && (
        <div style={{ padding: '14px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {activeTab === 'CONTROLS' ? (
            /* ── TAB 1: CONTROLS & SLICERS DECK ── */
            <>
              {/* Crime Slicers Section */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#C88A2C', fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>
                  <Filter size={12} color="#C88A2C" />
                  <span>Crime Slicers</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {/* Category Slicer */}
                  <div>
                    <label style={{ fontSize: '0.64rem', color: '#526058', fontWeight: 700, textTransform: 'uppercase' }}>Crime Category</label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => onCategoryChange(e.target.value)}
                      style={{
                        width: '100%',
                        backgroundColor: '#F4F0E8',
                        border: '1px solid #D4CEBF',
                        borderRadius: '6px',
                        color: '#132B20',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        padding: '5px 8px',
                        outline: 'none',
                        marginTop: '2px',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="ALL">All Categories ({dynamicFilters.categories.length})</option>
                      {dynamicFilters.categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  {/* Division Slicer */}
                  {dynamicFilters.divisions.length > 0 && (
                    <div>
                      <label style={{ fontSize: '0.64rem', color: '#526058', fontWeight: 700, textTransform: 'uppercase' }}>Division / Region</label>
                      <select
                        value={selectedDivision}
                        onChange={(e) => onDivisionChange(e.target.value)}
                        style={{
                          width: '100%',
                          backgroundColor: '#F4F0E8',
                          border: '1px solid #D4CEBF',
                          borderRadius: '6px',
                          color: '#132B20',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          padding: '5px 8px',
                          outline: 'none',
                          marginTop: '2px',
                          cursor: 'pointer'
                        }}
                      >
                        <option value="ALL">All Divisions ({dynamicFilters.divisions.length})</option>
                        {dynamicFilters.divisions.map(div => (
                          <option key={div} value={div}>{div}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Station Slicer */}
                  {dynamicFilters.stations.length > 0 && (
                    <div>
                      <label style={{ fontSize: '0.64rem', color: '#526058', fontWeight: 700, textTransform: 'uppercase' }}>Police Station</label>
                      <select
                        value={selectedStation}
                        onChange={(e) => onStationChange(e.target.value)}
                        style={{
                          width: '100%',
                          backgroundColor: '#F4F0E8',
                          border: '1px solid #D4CEBF',
                          borderRadius: '6px',
                          color: '#132B20',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          padding: '5px 8px',
                          outline: 'none',
                          marginTop: '2px',
                          cursor: 'pointer'
                        }}
                      >
                        <option value="ALL">All Stations ({dynamicFilters.stations.length})</option>
                        {dynamicFilters.stations.map(stn => (
                          <option key={stn} value={stn}>{stn}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Status Slicer */}
                  {dynamicFilters.statuses.length > 0 && (
                    <div>
                      <label style={{ fontSize: '0.64rem', color: '#526058', fontWeight: 700, textTransform: 'uppercase' }}>Case Status</label>
                      <select
                        value={selectedStatus}
                        onChange={(e) => onStatusChange(e.target.value)}
                        style={{
                          width: '100%',
                          backgroundColor: '#F4F0E8',
                          border: '1px solid #D4CEBF',
                          borderRadius: '6px',
                          color: '#132B20',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          padding: '5px 8px',
                          outline: 'none',
                          marginTop: '2px',
                          cursor: 'pointer'
                        }}
                      >
                        <option value="ALL">All Statuses ({dynamicFilters.statuses.length})</option>
                        {dynamicFilters.statuses.map(stat => (
                          <option key={stat} value={stat}>{stat}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              </div>

              {/* Layer Toggles Section */}
              <div style={{ borderTop: '1px solid #D4CEBF', paddingTop: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#C88A2C', fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>
                  <Layers size={12} color="#C88A2C" />
                  <span>Layer Overlays</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {/* 30 Districts Toggle */}
                  <div
                    onClick={onToggleDistricts}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '6px 10px',
                      backgroundColor: showDistricts ? '#EDE7DA' : '#FCFCFA',
                      border: `1px solid ${showDistricts ? '#C4B9A5' : '#D4CEBF'}`,
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.72rem',
                      fontWeight: showDistricts ? 700 : 500,
                      color: showDistricts ? '#132B20' : '#526058',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <span>30 Districts KGIS Polygons</span>
                    {showDistricts ? <Eye size={13} color="#0F5132" /> : <EyeOff size={13} color="#8A9A90" />}
                  </div>

                  {/* District Names Typography Toggle */}
                  {showDistricts && (
                    <div
                      onClick={onToggleDistrictLabels}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '6px 10px',
                        backgroundColor: showDistrictLabels ? '#EDE7DA' : '#FCFCFA',
                        border: `1px solid ${showDistrictLabels ? '#C4B9A5' : '#D4CEBF'}`,
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.72rem',
                        fontWeight: showDistrictLabels ? 700 : 500,
                        color: showDistrictLabels ? '#132B20' : '#526058',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <span>District Name Labels</span>
                      {showDistrictLabels ? <Eye size={13} color="#D49B44" /> : <EyeOff size={13} color="#8A9A90" />}
                    </div>
                  )}

                  {/* State Boundary Toggle */}
                  <div
                    onClick={onToggleStateBoundary}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '6px 10px',
                      backgroundColor: showStateBoundary ? '#EDE7DA' : '#FCFCFA',
                      border: `1px solid ${showStateBoundary ? '#C4B9A5' : '#D4CEBF'}`,
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.72rem',
                      fontWeight: showStateBoundary ? 700 : 500,
                      color: showStateBoundary ? '#132B20' : '#526058',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <span>Karnataka State Bound Vector</span>
                    {showStateBoundary ? <Eye size={13} color="#0F5132" /> : <EyeOff size={13} color="#8A9A90" />}
                  </div>
                </div>
              </div>

              {/* Live Incident KPI Metrics */}
              <div style={{ borderTop: '1px solid #D4CEBF', paddingTop: '10px' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#526058', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Live Incident Summary
                </div>
                <div style={{
                  backgroundColor: '#F4F0E8',
                  padding: '8px',
                  borderRadius: '8px',
                  border: '1px solid #D4CEBF',
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '6px'
                }}>
                  <div style={{ backgroundColor: '#FCFCFA', padding: '6px 8px', borderRadius: '6px', border: '1px solid #D4CEBF' }}>
                    <div style={{ fontSize: '0.62rem', color: '#526058', fontWeight: 600 }}>Plotted Cases</div>
                    <div style={{ fontSize: '0.94rem', fontWeight: 900, color: '#132B20', marginTop: '2px' }}>
                      {kpiSummary.total.toLocaleString()}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#FCFCFA', padding: '6px 8px', borderRadius: '6px', border: '1px solid #D4CEBF' }}>
                    <div style={{ fontSize: '0.62rem', color: '#526058', fontWeight: 600 }}>High Risk Hotspots</div>
                    <div style={{ fontSize: '0.94rem', fontWeight: 900, color: '#DC2626', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <Flame size={12} color="#DC2626" /> {kpiSummary.highRisk.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* ── TAB 2: INTELLIGENCE DOSSIER DECK ── */
            <>
              {selectedHotspot ? (
                /* Hotspot Intelligence Dossier */
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {/* Hotspot Header */}
                  <div style={{ borderBottom: '1px solid #D4CEBF', paddingBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: selectedHotspot.threat_color || '#DC2626',
                          display: 'inline-block'
                        }} />
                        <h4 style={{ margin: 0, fontSize: '0.88rem', fontWeight: 800, color: '#132B20' }}>
                          {selectedHotspot.name || 'DBSCAN Hotspot'}
                        </h4>
                      </div>
                      <button
                        onClick={onClearHotspot}
                        style={{ background: 'transparent', border: 'none', color: '#6B7A72', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 800 }}
                      >
                        ✕
                      </button>
                    </div>
                    <div style={{
                      display: 'inline-block',
                      marginTop: '4px',
                      fontSize: '0.62rem',
                      fontWeight: 900,
                      textTransform: 'uppercase',
                      color: selectedHotspot.threat_color || '#DC2626',
                      letterSpacing: '0.5px'
                    }}>
                      {selectedHotspot.threat_level || 'HIGH'} THREAT LEVEL
                    </div>
                  </div>

                  {/* Metrics */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                    <div style={{ backgroundColor: '#FCFCFA', padding: '6px 8px', borderRadius: '6px', border: '1px solid #D4CEBF' }}>
                      <div style={{ fontSize: '0.62rem', color: '#526058' }}>Volume</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 900, color: '#132B20' }}>
                        {selectedHotspot.incident_count} <span style={{ fontSize: '0.65rem', color: '#526058' }}>Cases</span>
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#FCFCFA', padding: '6px 8px', borderRadius: '6px', border: '1px solid #D4CEBF' }}>
                      <div style={{ fontSize: '0.62rem', color: '#526058' }}>Dominant Crime</div>
                      <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#0F5132', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {selectedHotspot.primary_crime}
                      </div>
                    </div>
                  </div>

                  {/* Primary Station */}
                  <div style={{ fontSize: '0.72rem', color: '#1F2937' }}>
                    <span style={{ color: '#526058', fontWeight: 700 }}>Jurisdiction:</span>{' '}
                    <b>{selectedHotspot.top_station || 'District HQ'}</b>
                  </div>

                  {/* Category Breakdown Tags */}
                  {selectedHotspot.category_breakdown && (
                    <div>
                      <div style={{ fontSize: '0.64rem', color: '#526058', fontWeight: 700, marginBottom: '5px', textTransform: 'uppercase' }}>
                        Category Distribution
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {Object.entries(selectedHotspot.category_breakdown).map(([cat, count]) => (
                          <span
                            key={cat}
                            style={{
                              backgroundColor: '#EAE4D6',
                              border: '1px solid #C4B9A5',
                              borderRadius: '5px',
                              padding: '2px 6px',
                              fontSize: '0.65rem',
                              color: '#132B20',
                              fontWeight: 700
                            }}
                          >
                            {cat}: {count}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* AI Leads */}
                  {selectedHotspot.llm_investigative_leads && (
                    <div style={{
                      backgroundColor: '#F4F0E8',
                      border: '1px solid #D4CEBF',
                      borderRadius: '8px',
                      padding: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#C88A2C', fontSize: '0.7rem', fontWeight: 800, marginBottom: '4px' }}>
                        <Sparkles size={12} color="#C88A2C" />
                        <span>AI Tactical Leads</span>
                      </div>
                      <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '0.66rem', color: '#2E3A33', lineHeight: 1.4 }}>
                        {selectedHotspot.llm_investigative_leads.map((lead, i) => (
                          <li key={i} style={{ marginBottom: '3px' }}>{lead}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action: Send to Conversational Agent */}
                  {(onStartInvestigation || onBackToChat) && (
                    <button
                      onClick={() => {
                        if (onStartInvestigation) {
                          onStartInvestigation(selectedHotspot);
                        } else if (onBackToChat) {
                          onBackToChat();
                        }
                      }}
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        backgroundColor: '#132B20',
                        color: '#FCFCFA',
                        border: '1px solid #132B20',
                        borderRadius: '7px',
                        padding: '8px',
                        fontSize: '0.72rem',
                        fontWeight: 800,
                        cursor: 'pointer',
                        boxShadow: '0 2px 8px rgba(19, 43, 32, 0.15)',
                        transition: 'all 0.15s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#0F5132';
                        e.currentTarget.style.borderColor = '#D49B44';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#132B20';
                        e.currentTarget.style.borderColor = '#132B20';
                      }}
                      title="Open Tactical AI Investigator with this Hotspot Context"
                    >
                      <Sparkles size={13} color="#D49B44" />
                      <span>Investigate with AI Agent</span>
                    </button>
                  )}
                </div>
              ) : selectedDistrictName ? (
                /* Selected District Card */
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #D4CEBF', paddingBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <ShieldCheck size={16} color="#D49B44" />
                      <h4 style={{ margin: 0, fontSize: '0.88rem', fontWeight: 800, color: '#132B20' }}>
                        {selectedDistrictName}
                      </h4>
                    </div>
                    <button
                      onClick={onClearDistrict}
                      style={{ background: 'transparent', border: 'none', color: '#6B7A72', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 800 }}
                    >
                      ✕
                    </button>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#526058', lineHeight: 1.4 }}>
                    District boundary polygon active. Use slicers on the left or click a Hotspot cluster to inspect localized incidents.
                  </div>
                </div>
              ) : (
                /* Empty Dossier Prompt */
                <div style={{ textAlign: 'center', padding: '24px 10px', color: '#64748b', fontSize: '0.72rem' }}>
                  <ShieldAlert size={28} color="#8A9A90" style={{ margin: '0 auto 8px', display: 'block' }} />
                  <b style={{ color: '#132B20', fontSize: '0.8rem' }}>No Hotspot Selected</b>
                  <p style={{ marginTop: '4px', lineHeight: 1.4, color: '#526058' }}>
                    Click any DBSCAN Hotspot polygon or district on the map canvas to open its deep-dive analytical dossier.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </aside>
  );
}
