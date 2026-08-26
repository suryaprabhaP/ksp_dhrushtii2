import React, { useState } from 'react';
import Chatbot from './components/Chatbot';
import AnalyticsDashboard from './analytics/AnalyticsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { initialDatasetState } from './analytics/services/datasetStore';
import { Shield, MapPin, Radio, BarChart2 } from 'lucide-react';

/**
 * STANDALONE CHATBOT UI MODULE ENTRY POINT
 * Supports seamless switching between Chatbot Console and Advanced Analytics Hub,
 * with shared dataset state across both interfaces.
 */
function App() {
  const [selectedDivision, setSelectedDivision] = useState('Bengaluru Division');
  const [activeView, setActiveView] = useState('chat'); // 'chat' | 'analytics'
  const [datasetState, setDatasetState] = useState(initialDatasetState);
  
  // MOCK LOGIN STATE
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return window.location.hash !== '#login';
  });
  const [badgeId, setBadgeId] = useState('OFFICER_BGL_001');
  const [password, setPassword] = useState('ksp2026');

  const handleLoginSubmit = (e) => {
    if (e) e.preventDefault();
    setIsLoggedIn(true);
    if (window.location.hash === '#login') {
      window.history.replaceState(null, '', window.location.pathname);
    }
  };

  const handleQuickBypass = () => {
    setIsLoggedIn(true);
    if (window.location.hash === '#login') {
      window.history.replaceState(null, '', window.location.pathname);
    }
  };

  const handleSignOut = () => {
    setIsLoggedIn(false);
    window.location.hash = '#login';
  };

  // Ingestion callback
  const handleDatasetLoaded = ({ filename, fileSizeBytes, sha256, headers, records }) => {
    setDatasetState(prev => ({
      ...prev,
      isLoaded: true,
      filename,
      fileSizeBytes,
      sha256,
      columns: headers,
      rawRecords: records,
      filteredRecords: records
    }));
  };

  // Filter slicer callbacks
  const handleUpdateFilters = (key, value) => {
    setDatasetState(prev => ({
      ...prev,
      filters: {
        ...prev.filters,
        [key]: value
      }
    }));
  };

  const handleResetFilters = () => {
    setDatasetState(prev => ({
      ...prev,
      filters: {
        division: 'All',
        district: 'All',
        crimeCategory: 'All',
        status: 'All',
        year: 'All',
        searchKeyword: ''
      }
    }));
  };

  // MOCK LOGIN PORTAL VIEW
  if (!isLoggedIn) {
    return (
      <ErrorBoundary>
        <div style={{
          width: '100vw',
          height: '100vh',
          backgroundColor: '#090d16',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: "'Inter', system-ui, sans-serif",
          color: '#f8fafc',
          padding: '20px'
        }}>
          <div style={{
            maxWidth: '460px',
            width: '100%',
            backgroundColor: '#0f172a',
            borderRadius: '20px',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            padding: '32px',
            boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
            textAlign: 'center'
          }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
              boxShadow: '0 0 20px rgba(37, 99, 235, 0.5)'
            }}>
              <Shield size={28} color="#ffffff" />
            </div>

            <h2 style={{ fontSize: '1.3rem', fontWeight: 900, margin: '0 0 4px 0', color: '#ffffff' }}>
              Karnataka State Police Portal
            </h2>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '24px' }}>
              Mock Officer Authentication & Command Console
            </div>

            <form onSubmit={handleLoginSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px', textAlign: 'left' }}>
              <div>
                <label style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>
                  Select Jurisdiction Division
                </label>
                <select
                  value={selectedDivision}
                  onChange={(e) => setSelectedDivision(e.target.value)}
                  style={{
                    width: '100%',
                    marginTop: '4px',
                    padding: '10px 12px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.82rem',
                    fontWeight: 700
                  }}
                >
                  <option value="Bengaluru Division">Bengaluru Division</option>
                  <option value="Mysuru Division">Mysuru Division</option>
                  <option value="Belagavi Division">Belagavi Division</option>
                  <option value="Kalaburagi Division">Kalaburagi Division</option>
                  <option value="State HQ Command">State HQ Command</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>
                  Officer Badge ID
                </label>
                <input
                  type="text"
                  value={badgeId}
                  onChange={(e) => setBadgeId(e.target.value)}
                  style={{
                    width: '100%',
                    marginTop: '4px',
                    padding: '10px 12px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.82rem',
                    fontWeight: 700
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>
                  Mock Security Passcode
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    marginTop: '4px',
                    padding: '10px 12px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.82rem',
                    fontWeight: 700
                  }}
                />
              </div>

              <button
                type="submit"
                style={{
                  marginTop: '8px',
                  width: '100%',
                  padding: '12px',
                  background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  fontSize: '0.85rem',
                  fontWeight: 800,
                  cursor: 'pointer',
                  boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)'
                }}
              >
                🛡️ Sign In to Command Console
              </button>
            </form>

            <div style={{ margin: '16px 0', borderTop: '1px solid #1e293b', position: 'relative' }}>
              <span style={{ position: 'absolute', top: '-9px', left: '50%', transform: 'translateX(-50%)', backgroundColor: '#0f172a', padding: '0 8px', fontSize: '0.65rem', color: '#64748b', fontWeight: 800 }}>OR</span>
            </div>

            <button
              onClick={handleQuickBypass}
              style={{
                width: '100%',
                padding: '11px',
                backgroundColor: 'rgba(34, 197, 94, 0.15)',
                color: '#4ade80',
                border: '1px solid rgba(34, 197, 94, 0.4)',
                borderRadius: '10px',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer'
              }}
            >
              ⚡ Quick Launch Assistant (Bypass Login)
            </button>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  if (activeView === 'analytics') {
    return (
      <ErrorBoundary>
        <AnalyticsDashboard
          divisionName={selectedDivision}
          onBackToChat={() => setActiveView('chat')}
          datasetState={datasetState}
          onDatasetLoaded={handleDatasetLoaded}
          onUpdateFilters={handleUpdateFilters}
          onResetFilters={handleResetFilters}
        />
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div style={{
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#090d16',
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        color: '#f8fafc'
      }}>
        {/* STANDALONE CHATBOT UI TOP BAR */}
        <header style={{
          height: '52px',
          background: 'linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
          borderBottom: '1px solid rgba(59, 130, 246, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 20px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
          zIndex: 50
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 12px rgba(37, 99, 235, 0.5)',
              border: '1px solid rgba(147, 197, 253, 0.4)'
            }}>
              <Shield size={20} color="#ffffff" />
            </div>
            <div>
              <h1 style={{
                margin: 0,
                fontSize: '1.05rem',
                fontWeight: 800,
                letterSpacing: '0.04em',
                background: 'linear-gradient(90deg, #ffffff 0%, #93c5fd 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                SENTINEL AI CHATBOT — STANDALONE UI MODULE
              </h1>
              <div style={{ fontSize: '0.65rem', color: '#64748b', fontWeight: 600, marginTop: '-2px' }}>
                React UI Component Module (`Chatbot.jsx` + `analytics/`)
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* VIEW SWITCHER IN TOP BAR */}
            <button
              onClick={() => setActiveView('analytics')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
                color: '#ffffff',
                border: '1px solid rgba(147, 197, 253, 0.4)',
                borderRadius: '8px',
                padding: '5px 12px',
                fontSize: '0.74rem',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 2px 10px rgba(37, 99, 235, 0.35)',
                transition: 'all 0.15s ease'
              }}
              title="Navigate to Advanced Crime Analytics Hub"
            >
              <BarChart2 size={13} />
              <span>📊 Analytics Hub {datasetState.isLoaded && `(${datasetState.rawRecords.length})`}</span>
            </button>

            {/* DIVISION SELECTOR */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              color: '#94a3b8'
            }}>
              <MapPin size={13} color="#60a5fa" />
              <span style={{ color: '#cbd5e1', fontWeight: 600 }}>Division:</span>
              <select
                value={selectedDivision}
                onChange={(e) => setSelectedDivision(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#60a5fa',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="Bengaluru Division" style={{ background: '#0f172a', color: '#f8fafc' }}>Bengaluru Division</option>
                <option value="Mysuru Division" style={{ background: '#0f172a', color: '#f8fafc' }}>Mysuru Division</option>
                <option value="Belagavi Division" style={{ background: '#0f172a', color: '#f8fafc' }}>Belagavi Division</option>
                <option value="Kalaburagi Division" style={{ background: '#0f172a', color: '#f8fafc' }}>Kalaburagi Division</option>
                <option value="State HQ Command" style={{ background: '#0f172a', color: '#f8fafc' }}>State HQ Command</option>
              </select>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              borderRadius: '20px',
              padding: '3px 10px',
              fontSize: '0.7rem',
              color: '#34d399',
              fontWeight: 700
            }}>
              <Radio size={12} color="#34d399" />
              <span>UI MODULE READY</span>
            </div>
          </div>
        </header>

        {/* CHATBOT UI COMPONENT CONTAINER */}
        <main style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
          <Chatbot
            divisionName={selectedDivision}
            onNavigateToAnalytics={() => setActiveView('analytics')}
            onDatasetIngested={handleDatasetLoaded}
            isDatasetLoaded={datasetState.isLoaded}
          />
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
