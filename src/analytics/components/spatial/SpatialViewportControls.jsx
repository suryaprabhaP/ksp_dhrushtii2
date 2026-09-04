import React from 'react';
import { Plus, Minus, Crosshair, RotateCcw } from 'lucide-react';

/**
 * SpatialViewportControls — Floating Bottom-Left Navigation Tools in DRISHTI Light Theme (SOLID: SRP)
 * Handles zoom in, zoom out, auto-fitting to dataset bounds, and resetting slicers.
 */
export default function SpatialViewportControls({
  onZoomIn,
  onZoomOut,
  onFitBounds,
  onResetFilters
}) {
  return (
    <div style={{
      position: 'absolute',
      bottom: '24px',
      left: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      zIndex: 999,
      pointerEvents: 'auto',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    }}>
      {/* Zoom In & Zoom Out Cluster */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#FCFCFA',
        border: '1px solid #D4CEBF',
        borderRadius: '8px',
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(19, 43, 32, 0.08)'
      }}>
        <button
          onClick={onZoomIn}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: '1px solid #D4CEBF',
            color: '#132B20',
            padding: '8px 10px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#EDE7DA';
            e.currentTarget.style.color = '#D49B44';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = '#132B20';
          }}
          title="Zoom In"
        >
          <Plus size={14} />
        </button>
        <button
          onClick={onZoomOut}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#132B20',
            padding: '8px 10px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#EDE7DA';
            e.currentTarget.style.color = '#D49B44';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = '#132B20';
          }}
          title="Zoom Out"
        >
          <Minus size={14} />
        </button>
      </div>

      {/* Auto-Fit Bounds Button */}
      <button
        onClick={onFitBounds}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: '#FCFCFA',
          border: '1px solid #D4CEBF',
          borderRadius: '8px',
          color: '#132B20',
          padding: '7px 11px',
          fontSize: '0.72rem',
          fontWeight: 800,
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(19, 43, 32, 0.08)',
          transition: 'all 0.15s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#EDE7DA';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#FCFCFA';
        }}
        title="Auto-Fit View to Plotted Coordinates"
      >
        <Crosshair size={13} color="#D49B44" />
        <span>Fit Bounds</span>
      </button>

      {/* Reset Slicers Button */}
      <button
        onClick={onResetFilters}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: '#FCFCFA',
          border: '1px solid #FECACA',
          borderRadius: '8px',
          color: '#DC2626',
          padding: '7px 11px',
          fontSize: '0.72rem',
          fontWeight: 700,
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(19, 43, 32, 0.08)',
          transition: 'all 0.15s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#FEE2E2';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#FCFCFA';
        }}
        title="Reset all slicers and viewport"
      >
        <RotateCcw size={13} color="#DC2626" />
        <span>Reset</span>
      </button>
    </div>
  );
}
