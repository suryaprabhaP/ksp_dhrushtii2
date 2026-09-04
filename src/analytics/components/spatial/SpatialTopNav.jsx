import React from 'react';
import {
  ArrowLeft,
  Compass,
  MapPin,
  Flame,
  ShieldAlert,
  Search,
  UploadCloud
} from 'lucide-react';

/**
 * SpatialTopNav — Slimline Command Header in DRISHTI Warm Parchment & Ivory Theme (SOLID: SRP)
 * Handles global navigation, view mode switching, search query input, and dataset modal trigger.
 */
export default function SpatialTopNav({
  onBackToChat,
  viewMode,
  onViewModeChange,
  hotspotsCount = 0,
  totalCoordinates = 0,
  searchQuery,
  onSearchChange,
  activeTileType,
  onTileTypeChange,
  onOpenUploader,
  activeDatasetsCount = 1
}) {
  return (
    <header style={{
      height: '52px',
      padding: '0 18px',
      backgroundColor: '#FCFCFA',
      borderBottom: '1px solid #D4CEBF',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '16px',
      zIndex: 1000,
      boxShadow: '0 4px 20px rgba(19, 43, 32, 0.06)'
    }}>
      {/* Left: Back Button & Branding */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 'fit-content' }}>
        {onBackToChat && (
          <button
            onClick={onBackToChat}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#EFEBE2',
              color: '#132B20',
              border: '1px solid #D4CEBF',
              borderRadius: '7px',
              padding: '5px 11px',
              fontSize: '0.74rem',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#EDE7DA';
              e.currentTarget.style.borderColor = '#C4B9A5';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#EFEBE2';
              e.currentTarget.style.borderColor = '#D4CEBF';
            }}
            title="Return to Conversational Chatbot Feed"
          >
            <ArrowLeft size={13} color="#132B20" />
            <span>Back</span>
          </button>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '30px',
            height: '30px',
            borderRadius: '8px',
            backgroundColor: '#132B20',
            border: '1px solid #D49B44',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 6px rgba(19, 43, 32, 0.15)'
          }}>
            <Compass size={16} color="#D49B44" />
          </div>
          <div>
            <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#132B20', letterSpacing: '0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>KSP SPATIAL RADAR</span>
              <span style={{
                backgroundColor: '#EAE4D6',
                color: '#8A5A18',
                fontSize: '0.66rem',
                fontWeight: 800,
                padding: '2px 8px',
                borderRadius: '10px',
                border: '1px solid #C4B9A5'
              }}>
                {totalCoordinates.toLocaleString()} Plotted
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Center: Segmented View Mode Switcher */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        backgroundColor: '#FCFCFA',
        border: '1px solid #D4CEBF',
        borderRadius: '8px',
        padding: '3px'
      }}>
        <button
          onClick={() => onViewModeChange('POINTS')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 10px',
            borderRadius: '6px',
            border: 'none',
            fontSize: '0.72rem',
            fontWeight: viewMode === 'POINTS' ? 800 : 600,
            cursor: 'pointer',
            backgroundColor: viewMode === 'POINTS' ? '#132B20' : 'transparent',
            color: viewMode === 'POINTS' ? '#FCFCFA' : '#526058',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            if (viewMode !== 'POINTS') e.currentTarget.style.backgroundColor = '#EDE7DA';
          }}
          onMouseLeave={(e) => {
            if (viewMode !== 'POINTS') e.currentTarget.style.backgroundColor = 'transparent';
          }}
          title="Display individual incident coordinate points"
        >
          <MapPin size={12} color={viewMode === 'POINTS' ? '#D49B44' : '#526058'} />
          <span>Points</span>
        </button>

        <button
          onClick={() => onViewModeChange('HEATMAP')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 10px',
            borderRadius: '6px',
            border: 'none',
            fontSize: '0.72rem',
            fontWeight: viewMode === 'HEATMAP' ? 800 : 600,
            cursor: 'pointer',
            backgroundColor: viewMode === 'HEATMAP' ? '#132B20' : 'transparent',
            color: viewMode === 'HEATMAP' ? '#FCFCFA' : '#526058',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            if (viewMode !== 'HEATMAP') e.currentTarget.style.backgroundColor = '#EDE7DA';
          }}
          onMouseLeave={(e) => {
            if (viewMode !== 'HEATMAP') e.currentTarget.style.backgroundColor = 'transparent';
          }}
          title="Display continuous density gradient heatmap"
        >
          <Flame size={12} color={viewMode === 'HEATMAP' ? '#D49B44' : '#526058'} />
          <span>Heatmap</span>
        </button>

        <button
          onClick={() => onViewModeChange('HOTSPOTS')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 10px',
            borderRadius: '6px',
            border: 'none',
            fontSize: '0.72rem',
            fontWeight: viewMode === 'HOTSPOTS' ? 800 : 600,
            cursor: 'pointer',
            backgroundColor: viewMode === 'HOTSPOTS' ? '#132B20' : 'transparent',
            color: viewMode === 'HOTSPOTS' ? '#FCFCFA' : '#526058',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            if (viewMode !== 'HOTSPOTS') e.currentTarget.style.backgroundColor = '#EDE7DA';
          }}
          onMouseLeave={(e) => {
            if (viewMode !== 'HOTSPOTS') e.currentTarget.style.backgroundColor = 'transparent';
          }}
          title="Run DBSCAN clustering to detect statistical crime hotspots"
        >
          <ShieldAlert size={12} color={viewMode === 'HOTSPOTS' ? '#D49B44' : '#526058'} />
          <span>Hotspots (DBSCAN)</span>
          {hotspotsCount > 0 && viewMode === 'HOTSPOTS' && (
            <span style={{
              backgroundColor: '#EAE4D6',
              color: '#DC2626',
              border: '1px solid #C4B9A5',
              borderRadius: '10px',
              padding: '0 5px',
              fontSize: '0.62rem',
              fontWeight: 900
            }}>
              {hotspotsCount}
            </span>
          )}
        </button>
      </div>

      {/* Right: Quick Search, Basemap, & Ingest */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Search Box */}
        <div style={{ position: 'relative', width: '180px' }}>
          <Search size={13} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: '#8A9A90' }} />
          <input
            type="text"
            placeholder="Search incident, station..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{
              width: '100%',
              backgroundColor: '#FCFCFA',
              border: '1px solid #D4CEBF',
              borderRadius: '7px',
              padding: '5px 8px 5px 26px',
              fontSize: '0.72rem',
              color: '#132B20',
              outline: 'none',
              transition: 'border-color 0.15s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#D49B44'}
            onBlur={(e) => e.target.style.borderColor = '#D4CEBF'}
          />
        </div>

        {/* Basemap Picker */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: '#EFEBE2',
          border: '1px solid #D4CEBF',
          borderRadius: '7px',
          padding: '2px 4px'
        }}>
          <button
            onClick={() => onTileTypeChange('VOYAGER')}
            style={{
              background: activeTileType === 'VOYAGER' ? '#132B20' : 'transparent',
              color: activeTileType === 'VOYAGER' ? '#FCFCFA' : '#526058',
              border: 'none',
              borderRadius: '5px',
              padding: '3px 7px',
              fontSize: '0.66rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            Voyager
          </button>
          <button
            onClick={() => onTileTypeChange('DARK')}
            style={{
              background: activeTileType === 'DARK' ? '#132B20' : 'transparent',
              color: activeTileType === 'DARK' ? '#FCFCFA' : '#526058',
              border: 'none',
              borderRadius: '5px',
              padding: '3px 7px',
              fontSize: '0.66rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            Dark
          </button>
        </div>

        {/* Ingest Dataset Trigger */}
        <button
          onClick={onOpenUploader}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#132B20',
            color: '#FCFCFA',
            border: '1px solid #132B20',
            borderRadius: '7px',
            padding: '5px 12px',
            fontSize: '0.72rem',
            fontWeight: 800,
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(19, 43, 32, 0.15)',
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
          title="Ingest CSV/KML files and manage active spatial dataset layers"
        >
          <UploadCloud size={13} color="#D49B44" />
          <span>Ingest</span>
          {activeDatasetsCount > 1 && (
            <span style={{
              backgroundColor: '#D49B44',
              color: '#111614',
              borderRadius: '10px',
              padding: '1px 5px',
              fontSize: '0.6rem',
              fontWeight: 900
            }}>
              {activeDatasetsCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
}
