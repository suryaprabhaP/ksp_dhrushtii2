import React, { useState } from 'react';
import Chatbot from './components/Chatbot';
import AnalyticsDashboard from './analytics/AnalyticsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import DraggableGlobalChat from './components/DraggableGlobalChat';
import ComplaintPortalContainer from './components/portals/EComplaint/ComplaintPortalContainer';
import PassportPortalContainer from './components/portals/PassportVerification/PassportPortalContainer';
import PoliceInitiatedPortalContainer from './components/portals/PoliceInitiated/PoliceInitiatedPortalContainer';
import CommandCenterMenu from './components/portals/CommandCenter/CommandCenterMenu';
import { GlobalInvestigationContextProvider } from './context/GlobalInvestigationContext';
import { initialDatasetState } from './analytics/services/datasetStore';
import { globalNetworkStore } from './analytics/services/networkAnalyticsService';
import { Shield, MapPin, Radio, BarChart2 } from 'lucide-react';
import CrimeAnalyticsHub from './components/portals/CrimeAnalyticsHub';

// KSP Main Division & Landing Components
import BengaluruHeadDashboard from './components/command_center/BengaluruHeadDashboard';
import MysuruHeadDashboard from './components/command_center/MysuruHeadDashboard';
import BelagaviHeadDashboard from './components/command_center/BelagaviHeadDashboard';
import KalaburagiHeadDashboard from './components/command_center/KalaburagiHeadDashboard';
import Login from './components/command_center/Login';
import DrishtiLanding from './ksp_drishti_landing/DrishtiLanding';

/**
 * STANDALONE CHATBOT UI MODULE ENTRY POINT
 * Supports seamless switching between Chatbot Console and Advanced Analytics Hub,
 * with shared dataset state across both interfaces.
 */
function ChatbotAppContainer({ selectedDivision, onNavigateBackToCommandCenter }) {
  const [activeView, setActiveView] = useState('chat'); // 'chat' | 'analytics' | 'ecomplaint' | 'passport' | 'police_fir'
  const [analyticsInitialTab, setAnalyticsInitialTab] = useState('dashboard');
  const [datasetState, setDatasetState] = useState(initialDatasetState);
  
  // Ingestion callback
  const handleDatasetLoaded = ({ filename, fileSizeBytes, sha256, headers, records }) => {
    // Synchronize both Tabular Store and Network Topology Graph Store
    globalNetworkStore.loadDataset(records, headers, filename);

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
    setDatasetState(prev => {
      const newFilters = { ...prev.filters, [key]: value };
      let filtered = [...prev.rawRecords];

      if (newFilters.division && newFilters.division !== 'All') {
        filtered = filtered.filter(r => (r.Division || r.division) === newFilters.division);
      }
      if (newFilters.district && newFilters.district !== 'All') {
        filtered = filtered.filter(r => (r.District || r.district) === newFilters.district);
      }
      if (newFilters.policeStation && newFilters.policeStation !== 'All') {
        filtered = filtered.filter(r => (r.Police_Station || r.police_station || r.Station) === newFilters.policeStation);
      }
      if (newFilters.crimeCategory && newFilters.crimeCategory !== 'All') {
        filtered = filtered.filter(r => (r.Crime_Category || r.crime_category || r.Category) === newFilters.crimeCategory);
      }
      if (newFilters.status && newFilters.status !== 'All') {
        filtered = filtered.filter(r => (r.Status || r.status) === newFilters.status);
      }
      if (newFilters.year && newFilters.year !== 'All') {
        filtered = filtered.filter(r => String(r.Year || r.year || (r.Date ? r.Date.split('-')[0] : '')) === String(newFilters.year));
      }
      if (newFilters.searchKeyword && newFilters.searchKeyword.trim()) {
        const kw = newFilters.searchKeyword.toLowerCase();
        filtered = filtered.filter(r => Object.values(r).some(val => String(val).toLowerCase().includes(kw)));
      }

      return {
        ...prev,
        filters: newFilters,
        filteredRecords: filtered
      };
    });
  };

  const handleResetFilters = () => {
    setDatasetState(prev => ({
      ...prev,
      filters: initialDatasetState.filters,
      filteredRecords: prev.rawRecords
    }));
  };

  // Central Session Reset Handler (SOLID: App.jsx orchestrates data lifecycle)
  const handleSessionReset = () => {
    globalNetworkStore.reset();
    setDatasetState(initialDatasetState);
  };

  // Central Session Restore Handler (SOLID: Restores full investigation context across tabs)
  const handleRestoreSessionData = (savedDatasetState) => {
    if (savedDatasetState && savedDatasetState.isLoaded && savedDatasetState.rawRecords?.length > 0) {
      setDatasetState(savedDatasetState);
      const headers = savedDatasetState.columns || Object.keys(savedDatasetState.rawRecords[0] || {});
      globalNetworkStore.loadDataset(
        savedDatasetState.rawRecords,
        headers,
        savedDatasetState.filename || 'Restored Investigation'
      );
    } else {
      handleSessionReset();
    }
  };

  if (activeView === 'ecomplaint') {
    return (
      <ErrorBoundary>
        <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
          <ComplaintPortalContainer onBackToDashboard={() => setActiveView('chat')} />
          <DraggableGlobalChat divisionName={selectedDivision} />
        </div>
      </ErrorBoundary>
    );
  }

  if (activeView === 'passport') {
    return (
      <ErrorBoundary>
        <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
          <PassportPortalContainer onBackToDashboard={() => setActiveView('chat')} />
          <DraggableGlobalChat divisionName={selectedDivision} />
        </div>
      </ErrorBoundary>
    );
  }

  if (activeView === 'police_fir') {
    return (
      <ErrorBoundary>
        <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
          <PoliceInitiatedPortalContainer onBackToDashboard={() => setActiveView('chat')} />
          <DraggableGlobalChat divisionName={selectedDivision} />
        </div>
      </ErrorBoundary>
    );
  }

  if (activeView === 'analytics') {
    return (
      <ErrorBoundary>
        <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
          <AnalyticsDashboard
            divisionName={selectedDivision}
            onBackToChat={() => setActiveView('chat')}
            datasetState={datasetState}
            initialTab={analyticsInitialTab}
            onDatasetLoaded={handleDatasetLoaded}
            onUpdateFilters={handleUpdateFilters}
            onResetFilters={handleResetFilters}
          />
          <DraggableGlobalChat divisionName={selectedDivision} />
        </div>
      </ErrorBoundary>
    );
  }

  if (activeView === 'crime_analytics_hub') {
    return (
      <ErrorBoundary>
        <CrimeAnalyticsHub
          selectedDivision={selectedDivision}
          onNavigateBackToCommandCenter={() => setActiveView('chat')}
          isDatasetLoaded={datasetState.isLoaded}
          datasetState={datasetState}
          onDatasetIngested={handleDatasetLoaded}
          onSessionReset={handleSessionReset}
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
        color: '#f8fafc',
        position: 'relative'
      }}>
        {/* TOP COMMAND BAR (TACTICAL FOREST GREEN & GOLD THEME) */}
        <header style={{
          height: '50px',
          background: 'linear-gradient(90deg, #0A130E 0%, #132B20 50%, #0A130E 100%)',
          borderBottom: '1px solid rgba(212, 155, 68, 0.35)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 18px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
          zIndex: 50
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div 
              style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
              onClick={onNavigateBackToCommandCenter}
              title="Click to return to KSP Main Command GIS Portal"
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #132B20 0%, #1E4332 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 12px rgba(212, 155, 68, 0.35)',
                border: '1px solid #D49B44'
              }}>
                <Shield size={18} color="#D49B44" />
              </div>
              <h1 style={{
                margin: 0,
                fontSize: '0.95rem',
                fontFamily: "'Outfit', sans-serif",
                fontWeight: 900,
                letterSpacing: '0.6px',
                background: 'linear-gradient(90deg, #FCFCFA 0%, #E8C17C 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                KSP DRISHTI
              </h1>
            </div>

            {/* UNIFIED COMMAND CENTER BUTTON (DIRECT ROUTE TO MAIN GIS LAYER) */}
            <CommandCenterMenu onNavigateBackToCommandCenter={onNavigateBackToCommandCenter} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* DIVISION INFO */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(19, 43, 32, 0.85)',
              border: '1px solid rgba(212, 155, 68, 0.35)',
              borderRadius: '8px',
              padding: '3px 9px',
              fontSize: '0.72rem',
              color: '#889E90'
            }}>
              <MapPin size={12} color="#D49B44" />
              <span style={{ color: '#CBD5E1', fontWeight: 600 }}>Division:</span>
              <span style={{ color: '#D49B44', fontWeight: 700 }}>{selectedDivision}</span>
            </div>

            {/* STATUS BADGE */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              borderRadius: '20px',
              padding: '3px 9px',
              fontSize: '0.68rem',
              color: '#34D399',
              fontWeight: 700
            }}>
              <Radio size={11} color="#34D399" />
              <span>COMMAND READY</span>
            </div>

            {/* ZOHO ANALYTICS SPLIT-SCREEN HUB TOGGLE BUTTON */}
            <button
              onClick={() => setActiveView('crime_analytics_hub')}
              style={{
                background: 'linear-gradient(135deg, #1d4ed8, #0284c7)',
                border: '1px solid rgba(56, 189, 248, 0.4)',
                borderRadius: '6px',
                padding: '4px 10px',
                color: '#ffffff',
                fontSize: '0.68rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                boxShadow: '0 0 10px rgba(56, 189, 248, 0.3)'
              }}
              title="Launch Dual-Console Zoho Analytics Split-Screen Studio"
            >
              <BarChart2 size={12} color="#ffffff" />
              <span>ZOHO ANALYTICS HUB</span>
            </button>
          </div>
        </header>

        {/* CHATBOT UI COMPONENT CONTAINER */}
        <main style={{ flex: 1, position: 'relative', overflow: 'hidden', height: 'calc(100vh - 52px)' }}>
          <Chatbot
            divisionName={selectedDivision}
            onNavigateToAnalytics={() => { setAnalyticsInitialTab('dashboard'); setActiveView('analytics'); }}
            onNavigateToNetwork={() => { setAnalyticsInitialTab('network_graph'); setActiveView('analytics'); }}
            onNavigateBackToCommandCenter={onNavigateBackToCommandCenter}
            onDatasetIngested={handleDatasetLoaded}
            onSessionReset={handleSessionReset}
            onRestoreSessionData={handleRestoreSessionData}
            isDatasetLoaded={datasetState.isLoaded}
            datasetState={datasetState}
          />
        </main>
        
        {/* DRAGGABLE GLOBAL CHAT OVERLAY */}
        <DraggableGlobalChat divisionName={selectedDivision} />
      </div>
    </ErrorBoundary>
  );
}

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  
  // Controls the main view: 'main_command' (GIS Map) vs 'chatbot' (Assistant)
  const [appActiveView, setAppActiveView] = useState('main_command');

  const handleLoginSuccess = (userAuthData) => {
    setCurrentUser(userAuthData);
    setIsAuthenticated(true);
    setAppActiveView('main_command'); // Default to main GIS command after login
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  const navigateToChatbot = () => {
    setAppActiveView('chatbot');
  };

  const navigateToMainCommand = () => {
    setAppActiveView('main_command');
  };

  // 1. Initial Interactive Landing Experience
  if (isLoading) {
    return <DrishtiLanding onComplete={() => setIsLoading(false)} />;
  }

  // 2. Authentication Entry Point
  if (!isAuthenticated) {
    return <Login onLogin={handleLoginSuccess} />;
  }

  // 3. Chatbot Layer
  if (appActiveView === 'chatbot') {
    return (
      <GlobalInvestigationContextProvider>
        <ChatbotAppContainer 
          selectedDivision={currentUser?.division?.name || 'Bengaluru Division'} 
          onNavigateBackToCommandCenter={navigateToMainCommand}
        />
      </GlobalInvestigationContextProvider>
    );
  }

  // 4. Main Landing Layer (Division GIS Dashboards)
  const username = currentUser?.username || '';
  const divId = currentUser?.division?.id || '';

  const isBengaluruUser = username === 'ksp.bengaluru.head' || username.startsWith('ksp.bengaluru') || username.startsWith('ksp.chikkaballapura') || username.startsWith('ksp.chitradurga') || username.startsWith('ksp.davanagere') || username.startsWith('ksp.kolar') || username.startsWith('ksp.kgf') || username.startsWith('ksp.ramanagara') || username.startsWith('ksp.tumakuru') || divId === 'bengaluru';
  const isMysuruUser = username === 'ksp.mysuru.head' || username.startsWith('ksp.mysuru') || username.startsWith('ksp.chamarajanagara') || username.startsWith('ksp.chikkamagaluru') || username.startsWith('ksp.dakshina.kannada') || username.startsWith('ksp.hassan') || username.startsWith('ksp.kodagu') || username.startsWith('ksp.mandya') || username.startsWith('ksp.udupi') || divId === 'mysuru';
  const isBelagaviUser = username === 'ksp.belagavi.head' || username.startsWith('ksp.belagavi') || username.startsWith('ksp.bagalkote') || username.startsWith('ksp.dharwad') || username.startsWith('ksp.gadag') || username.startsWith('ksp.haveri') || username.startsWith('ksp.uttara.kannada') || username.startsWith('ksp.vijayapura') || divId === 'belagavi';
  const isKalaburagiUser = username === 'ksp.kalaburagi.head' || username.startsWith('ksp.kalaburagi') || username.startsWith('ksp.ballari') || username.startsWith('ksp.bidar') || username.startsWith('ksp.koppal') || username.startsWith('ksp.raichur') || username.startsWith('ksp.vijayanagara') || username.startsWith('ksp.yadgir') || divId === 'kalaburagi';

  if (isBengaluruUser) {
    return <BengaluruHeadDashboard currentUser={currentUser} onLogout={handleLogout} onNavigateToChatbot={navigateToChatbot} />;
  }

  if (isMysuruUser) {
    return <MysuruHeadDashboard currentUser={currentUser} onLogout={handleLogout} onNavigateToChatbot={navigateToChatbot} />;
  }

  if (isBelagaviUser) {
    return <BelagaviHeadDashboard currentUser={currentUser} onLogout={handleLogout} onNavigateToChatbot={navigateToChatbot} />;
  }

  if (isKalaburagiUser) {
    return <KalaburagiHeadDashboard currentUser={currentUser} onLogout={handleLogout} onNavigateToChatbot={navigateToChatbot} />;
  }

  // Fallback to Bengaluru if authenticated
  return <BengaluruHeadDashboard currentUser={currentUser} onLogout={handleLogout} onNavigateToChatbot={navigateToChatbot} />;
}
