import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable';
import { 
  ShieldAlert, 
  X, 
  Minus, 
  Maximize2, 
  Send, 
  Bot, 
  User, 
  GripHorizontal, 
  Compass, 
  CheckCircle, 
  AlertTriangle,
  FileSpreadsheet,
  Search,
  Sparkles,
  Ticket
} from 'lucide-react';
import { useGlobalInvestigation } from '../context/GlobalInvestigationContext';
import { getApiUrl } from '../services/apiClient';

export default function DraggableGlobalChat({ divisionName = "Bengaluru Division" }) {
  const { isOverlayOpen, isMinimized, spatialPayload, closeInvestigation, toggleMinimize } = useGlobalInvestigation();
  const nodeRef = useRef(null);
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const district = spatialPayload?.spatial_context?.district_name || divisionName || "Bengaluru Urban";
  const threatLevel = spatialPayload?.hotspot_metadata?.threat_level || "CRITICAL";
  const incidentCount = spatialPayload?.hotspot_metadata?.incident_count || 0;

  // Initialize or update dialogue when spatial payload is injected
  useEffect(() => {
    if (spatialPayload && isOverlayOpen) {
      const initialGreeting = {
        id: `sys_${Date.now()}`,
        sender: 'bot',
        agent_label: 'Tactical Spatial Agent 📍',
        agent_color: '#D49B44',
        agent_icon: '🛡️',
        text: `### 📍 Tactical Geospatial Context Injected: **${district}**\n\n` +
              `**Operational Sector Threat:** \`${threatLevel}\` | **Geotagged Incidents:** \`${incidentCount}\`\n\n` +
              `I have synchronized this active geospatial cluster into the **Global Chat Session Memory**.\n\n` +
              `**Available Tactical Directives:**\n` +
              `1. 🔍 **Query Zoho CRM**: Cross-reference active warrants and repeat suspects.\n` +
              `2. 🎫 **Dispatch Zoho Desk**: Log an automated P1 Tactical Dispatch ticket.\n` +
              `3. 📊 **Multi-Disciplinary Analysis**: Analyze crime categories against loss metrics.\n\n` +
              `*How would you like to coordinate this field operation, Officer?*`
      };
      setMessages((prev) => (prev.length === 0 ? [initialGreeting] : [...prev, initialGreeting]));
    }
  }, [spatialPayload, isOverlayOpen, district, threatLevel, incidentCount]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (!isOverlayOpen) return null;

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsg = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch(getApiUrl('/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          division: district,
          session_id: `global_session_${district.toLowerCase().replace(/\s+/g, '_')}`,
          context_injection: spatialPayload
        })
      });

      const data = await response.json();
      const botMsg = {
        id: `bot_${Date.now()}`,
        sender: 'bot',
        agent_label: data.agent_label || 'Sentinel Tactical AI',
        agent_color: data.agent_color || '#D49B44',
        agent_icon: data.agent_icon || '🛡️',
        text: data.answer || 'Response synthesized.',
        provider: data.provider || 'orchestrator'
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Global Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'bot',
          agent_label: 'Sentinel Tactical AI',
          agent_color: '#ef4444',
          agent_icon: '⚠️',
          text: `### ⚠️ Dispatch Connection Error\n\nFailed to reach Master Chatbot Router. Error: \`${err.message}\``
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Draggable
      nodeRef={nodeRef}
      handle=".drag-handle"
      defaultPosition={{ x: window.innerWidth > 1200 ? window.innerWidth - 560 : 60, y: 80 }}
      bounds="body"
    >
      <div
        ref={nodeRef}
        style={{
          position: 'fixed',
          zIndex: 99999,
          width: isMinimized ? '340px' : '520px',
          maxHeight: isMinimized ? '58px' : '82vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(13, 21, 18, 0.98)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(212, 155, 68, 0.35)',
          borderRadius: '16px',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(19, 43, 32, 0.4)',
          overflow: 'hidden',
          transition: 'width 0.2s ease, max-height 0.2s ease',
          color: '#FCFCFA',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}
      >
        {/* TOP DRAG HANDLE HEADER */}
        <div
          className="drag-handle"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 16px',
            background: 'linear-gradient(90deg, #132B20 0%, #0D1512 100%)',
            borderBottom: isMinimized ? 'none' : '1px solid rgba(212, 155, 68, 0.3)',
            cursor: 'grab',
            userSelect: 'none'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GripHorizontal size={16} color="#D49B44" />
            <ShieldAlert size={18} color="#D49B44" />
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#FCFCFA', letterSpacing: '0.5px' }}>
              TACTICAL OVERLAY <span style={{ color: '#D49B44', fontSize: '0.72rem', fontWeight: 600 }}>({district})</span>
            </span>
            <span
              style={{
                fontSize: '0.62rem',
                fontWeight: 800,
                padding: '2px 6px',
                borderRadius: '4px',
                background: threatLevel === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(212, 155, 68, 0.2)',
                color: threatLevel === 'CRITICAL' ? '#fca5a5' : '#D49B44',
                border: threatLevel === 'CRITICAL' ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(212, 155, 68, 0.4)'
              }}
            >
              {threatLevel}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <button
              onClick={toggleMinimize}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: 'none',
                color: '#8A9A90',
                borderRadius: '6px',
                padding: '4px',
                cursor: 'pointer'
              }}
              title={isMinimized ? "Maximize" : "Minimize"}
            >
              {isMinimized ? <Maximize2 size={14} /> : <Minus size={14} />}
            </button>
            <button
              onClick={closeInvestigation}
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: 'none',
                color: '#f87171',
                borderRadius: '6px',
                padding: '4px',
                cursor: 'pointer'
              }}
              title="Close"
            >
              <X size={14} />
            </button>
          </div>
        </div>

        {/* EXPANDED CONTENT BODY */}
        {!isMinimized && (
          <>
            {/* CONTEXT STATUS STRIP */}
            <div
              style={{
                padding: '6px 14px',
                background: '#101A16',
                borderBottom: '1px solid rgba(212, 155, 68, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.68rem',
                color: '#8A9A90'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Compass size={12} color="#D49B44" />
                <span>Geospatial Hotspot Context Synced</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#10B981', fontWeight: 600 }}>● Zoho CRM Connected</span>
                <span style={{ color: '#D49B44', fontWeight: 600 }}>● Zoho Desk Linked</span>
              </div>
            </div>

            {/* CHAT MESSAGES STREAM */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                minHeight: '260px',
                maxHeight: '440px',
                background: '#0D1512'
              }}
            >
              {messages.map((m) => (
                <div
                  key={m.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '92%'
                  }}
                >
                  {m.sender === 'bot' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', fontSize: '0.72rem', fontWeight: 700, color: m.agent_color || '#D49B44' }}>
                      <span>{m.agent_icon || '🛡️'}</span>
                      <span>{m.agent_label || 'Sentinel Tactical AI'}</span>
                    </div>
                  )}

                  <div
                    style={{
                      padding: '10px 14px',
                      borderRadius: m.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                      background: m.sender === 'user' ? 'linear-gradient(135deg, #1E4332 0%, #132B20 100%)' : '#16231D',
                      border: m.sender === 'user' ? '1px solid rgba(212, 155, 68, 0.4)' : '1px solid rgba(212, 155, 68, 0.25)',
                      color: '#FCFCFA',
                      fontSize: '0.78rem',
                      lineHeight: '1.45',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.35)'
                    }}
                  >
                    <div
                      style={{ whiteSpace: 'pre-wrap' }}
                      dangerouslySetInnerHTML={{
                        __html: m.text
                          .replace(/### (.*?)\n/g, '<div style="font-weight:800; color:#D49B44; margin-bottom:4px; font-size:0.85rem;">$1</div>')
                          .replace(/#### (.*?)\n/g, '<div style="font-weight:700; color:#E8C17C; margin-top:6px; margin-bottom:2px;">$1</div>')
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\*(.*?)\*/g, '<em>$1</em>')
                          .replace(/`([^`]+)`/g, '<code style="background:rgba(0,0,0,0.5); padding:1px 4px; border-radius:3px; color:#D49B44; font-family:monospace;">$1</code>')
                      }}
                    />
                  </div>
                </div>
              ))}

              {loading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 12px', background: '#16231D', border: '1px solid rgba(212, 155, 68, 0.2)', borderRadius: '8px', width: 'fit-content' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#D49B44', animation: 'pulse 1s infinite' }} />
                  <span style={{ fontSize: '0.72rem', color: '#8A9A90' }}>Tactical Orchestrator synthesizing directive...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* QUICK TACTICAL ACTION CHIPS */}
            <div
              style={{
                display: 'flex',
                gap: '6px',
                padding: '6px 12px',
                overflowX: 'auto',
                background: '#0D1512',
                borderTop: '1px solid rgba(212, 155, 68, 0.15)'
              }}
            >
              <button
                onClick={() => handleSendMessage(`Query Zoho CRM for repeat suspects and syndicate targets operating in ${district}.`)}
                style={{
                  background: '#1A2C24',
                  border: '1px solid rgba(212, 155, 68, 0.35)',
                  color: '#D49B44',
                  borderRadius: '12px',
                  padding: '3px 8px',
                  fontSize: '0.66rem',
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Search size={11} color="#D49B44" /> 🔍 Check Repeat Suspects (Zoho CRM)
              </button>

              <button
                onClick={() => handleSendMessage(`Log a critical priority tactical dispatch ticket in Zoho Desk for ${district}.`)}
                style={{
                  background: '#1A2C24',
                  border: '1px solid rgba(16, 185, 129, 0.35)',
                  color: '#10B981',
                  borderRadius: '12px',
                  padding: '3px 8px',
                  fontSize: '0.66rem',
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Ticket size={11} color="#10B981" /> 🎫 Dispatch Alert (Zoho Desk)
              </button>

              <button
                onClick={() => handleSendMessage(`Formulate a Section 102 BNSS tactical checkpoint grid for ${district}.`)}
                style={{
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.35)',
                  color: '#fca5a5',
                  borderRadius: '12px',
                  padding: '3px 8px',
                  fontSize: '0.66rem',
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <AlertTriangle size={11} color="#fca5a5" /> 🚨 Suggest Patrol Grid
              </button>
            </div>

            {/* CHAT INPUT FORM */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{
                display: 'flex',
                gap: '8px',
                padding: '10px 14px',
                background: '#101A16',
                borderTop: '1px solid rgba(212, 155, 68, 0.2)'
              }}
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={`Ask tactical intelligence about ${district}...`}
                style={{
                  flex: 1,
                  background: '#121F19',
                  border: '1px solid #284436',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#FCFCFA',
                  fontSize: '0.78rem',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                disabled={loading || !inputMessage.trim()}
                style={{
                  background: 'linear-gradient(135deg, #10B981 0%, #132B20 100%)',
                  color: '#FCFCFA',
                  border: '1px solid rgba(212, 155, 68, 0.4)',
                  borderRadius: '8px',
                  padding: '0 14px',
                  fontWeight: 800,
                  fontSize: '0.78rem',
                  cursor: loading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !inputMessage.trim() ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Send size={13} color="#D49B44" />
              </button>
            </form>
          </>
        )}
      </div>
    </Draggable>
  );
}
