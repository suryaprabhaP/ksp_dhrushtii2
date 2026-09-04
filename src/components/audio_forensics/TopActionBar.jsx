import React from 'react';
import { ArrowLeft, Mic, Shield, PlusCircle } from 'lucide-react';
import { VIEW_STATES } from './constants';

/**
 * TopActionBar — Top Navigation & Session Status for Audio Forensics Panel
 * (SOLID: SRP — Header presentation & route controls in DRISHTI Light Theme)
 */
export default function TopActionBar({
  sessionId,
  divisionName,
  viewState,
  onBackToChat,
  onUploadAnother,
  isUploading,
  isStreaming
}) {
  return (
    <div style={{
      height: '58px',
      borderBottom: '1px solid #D4CEBF',
      backgroundColor: '#FCFCFA',
      boxShadow: '0 4px 18px rgba(19, 43, 32, 0.05)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      flexShrink: 0,
      zIndex: 20
    }}>
      {/* Left: Back button & Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <button
          onClick={onBackToChat}
          style={{
            background: '#EFEBE2',
            border: '1px solid #D4CEBF',
            color: '#132B20',
            borderRadius: '8px',
            padding: '6px 12px',
            fontSize: '0.78rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
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
        >
          <ArrowLeft size={14} color="#132B20" /> Back to Chatbot
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '34px',
            height: '34px',
            borderRadius: '8px',
            backgroundColor: '#132B20',
            border: '1px solid #D49B44',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(19, 43, 32, 0.15)'
          }}>
            <Mic size={18} color="#D49B44" />
          </div>
          <div>
            <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#132B20', letterSpacing: '0.02em' }}>
              AUDIO FORENSIC INTELLIGENCE STUDIO
            </div>
            <div style={{ fontSize: '0.66rem', color: '#526058', fontWeight: 600 }}>
              Zoho Zia STT Speech Engine • Spotify-Style Bilingual Lyrics • Sandboxed RAG Staging
            </div>
          </div>
        </div>
      </div>

      {/* Right: Actions, Session Info, Division */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {viewState === VIEW_STATES.TRANSCRIPT_ACTIVE && (
          <button
            disabled={isUploading || isStreaming}
            onClick={onUploadAnother}
            style={{
              backgroundColor: '#132B20',
              border: '1px solid #132B20',
              color: '#FCFCFA',
              borderRadius: '8px',
              padding: '6px 14px',
              fontSize: '0.78rem',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: isUploading || isStreaming ? 'not-allowed' : 'pointer',
              opacity: isUploading || isStreaming ? 0.6 : 1,
              boxShadow: '0 2px 8px rgba(19, 43, 32, 0.15)',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!isUploading && !isStreaming) {
                e.currentTarget.style.backgroundColor = '#0F5132';
                e.currentTarget.style.borderColor = '#D49B44';
              }
            }}
            onMouseLeave={(e) => {
              if (!isUploading && !isStreaming) {
                e.currentTarget.style.backgroundColor = '#132B20';
                e.currentTarget.style.borderColor = '#132B20';
              }
            }}
            title="Discard current unconfirmed transcript and upload a new audio file"
          >
            <PlusCircle size={14} color="#D49B44" /> Upload Another Audio
          </button>
        )}

        <div style={{
          fontSize: '0.72rem',
          backgroundColor: '#EAE4D6',
          border: '1px solid #C4B9A5',
          color: '#8A5A18',
          padding: '4px 10px',
          borderRadius: '6px',
          fontWeight: 700
        }}>
          Session: <span style={{ color: '#132B20', fontWeight: 800 }}>{sessionId}</span>
        </div>

        <div style={{
          fontSize: '0.72rem',
          backgroundColor: '#EAE4D6',
          border: '1px solid #C4B9A5',
          color: '#132B20',
          padding: '4px 10px',
          borderRadius: '6px',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <Shield size={13} color="#0F5132" /> {divisionName}
        </div>
      </div>
    </div>
  );
}
