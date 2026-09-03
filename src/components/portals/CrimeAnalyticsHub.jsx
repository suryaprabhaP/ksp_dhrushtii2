import React, { useState } from 'react';
import VisualIntelligenceStudio from '../VisualIntelligenceStudio';
import Chatbot from '../Chatbot';
import { Shield, BarChart2, MessageSquare, ArrowLeft } from 'lucide-react';

/**
 * CrimeAnalyticsHub (SOLID - Composition)
 * Unified Side-by-Side Command View:
 * - Left Pane: Zoho Analytics Interactive Studio (65% width)
 * - Right Pane: Drishti Conversational AI Co-Pilot (35% width)
 */
export default function CrimeAnalyticsHub({
  selectedDivision = "Bengaluru Division",
  onNavigateBackToCommandCenter,
  isDatasetLoaded = true,
  datasetState = null,
  onDatasetIngested,
  onSessionReset
}) {
  const [splitRatio, setSplitRatio] = useState(65); // Default 65% Analytics, 35% Chatbot

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#090d16',
      color: '#f8fafc',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    }}>
      {/* ── TOP HUB COMMAND BAR ──────────────────────────────────────────────── */}
      <header style={{
        height: '48px',
        backgroundColor: '#0a130e',
        borderBottom: '1px solid rgba(212, 155, 68, 0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        flexShrink: 0,
        zIndex: 40
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {onNavigateBackToCommandCenter && (
            <button
              onClick={onNavigateBackToCommandCenter}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(212, 155, 68, 0.3)',
                color: '#d49b44',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.72rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              title="Return to Main GIS Command Center"
            >
              <ArrowLeft size={13} /> Back to GIS Command
            </button>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, #132b20, #1e4332)',
              border: '1px solid #d49b44',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Shield size={14} color="#d49b44" />
            </div>
            <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#fcfcfa', letterSpacing: '0.4px' }}>
              CRIME ANALYTICS HUB
            </span>
            <span style={{ fontSize: '0.65rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '1px 6px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
              Zoho Analytics Dual-Console
            </span>
          </div>
        </div>

        {/* VIEW RATIO TOGGLES */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ fontSize: '0.68rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Split:</span>
            <button
              onClick={() => setSplitRatio(50)}
              style={{
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: splitRatio === 50 ? '#1e3a8a' : 'transparent',
                color: splitRatio === 50 ? '#38bdf8' : '#94a3b8',
                fontSize: '0.65rem',
                cursor: 'pointer'
              }}
            >
              50 / 50
            </button>
            <button
              onClick={() => setSplitRatio(65)}
              style={{
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: splitRatio === 65 ? '#1e3a8a' : 'transparent',
                color: splitRatio === 65 ? '#38bdf8' : '#94a3b8',
                fontSize: '0.65rem',
                cursor: 'pointer'
              }}
            >
              65 / 35
            </button>
            <button
              onClick={() => setSplitRatio(80)}
              style={{
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: splitRatio === 80 ? '#1e3a8a' : 'transparent',
                color: splitRatio === 80 ? '#38bdf8' : '#94a3b8',
                fontSize: '0.65rem',
                cursor: 'pointer'
              }}
            >
              80 / 20
            </button>
          </div>
        </div>
      </header>

      {/* ── SPLIT WORKSPACE BODY ──────────────────────────────────────────────── */}
      <div style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden',
        width: '100%',
        height: 'calc(100% - 48px)'
      }}>
        {/* LEFT PANE: ZOHO ANALYTICS STUDIO */}
        <div style={{
          width: `${splitRatio}%`,
          height: '100%',
          overflow: 'hidden',
          transition: 'width 0.2s ease-in-out'
        }}>
          <VisualIntelligenceStudio
            divisionName={selectedDivision}
            isDatasetLoaded={isDatasetLoaded}
            datasetCount={datasetState?.rawRecords ? datasetState.rawRecords.length : 0}
          />
        </div>

        {/* RIGHT PANE: DRISHTI CONVERSATIONAL ASSISTANT */}
        <div style={{
          width: `${100 - splitRatio}%`,
          height: '100%',
          overflow: 'hidden',
          borderLeft: '1px solid rgba(59, 130, 246, 0.25)',
          transition: 'width 0.2s ease-in-out'
        }}>
          <Chatbot
            divisionName={selectedDivision}
            isDatasetLoaded={isDatasetLoaded}
            datasetState={datasetState}
            onDatasetIngested={onDatasetIngested}
            onSessionReset={onSessionReset}
            onNavigateBackToCommandCenter={onNavigateBackToCommandCenter}
          />
        </div>
      </div>
    </div>
  );
}
