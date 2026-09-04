import React from 'react';
import { Shield, CheckCircle2 } from 'lucide-react';

/**
 * AudioGatewayModal — Human-in-the-Loop Evidentiary Chain-of-Custody Modal in DRISHTI Light Theme
 * (SOLID: SRP — Confirmation Gateway Presentation)
 */
export default function AudioGatewayModal({
  isOpen,
  sessionId,
  isInjecting,
  onCancel,
  onConfirm
}) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(19, 43, 32, 0.45)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 99999,
      animation: 'fadeIn 0.2s ease-out'
    }}>
      <div style={{
        maxWidth: '520px',
        width: '90%',
        backgroundColor: '#F4F0E8',
        border: '1px solid #D4CEBF',
        borderRadius: '20px',
        padding: '28px',
        boxShadow: '0 20px 45px rgba(19, 43, 32, 0.15)',
        color: '#132B20',
        fontFamily: "'Inter', system-ui, sans-serif"
      }}>
        {/* Header Icon + Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            backgroundColor: '#132B20',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #D49B44',
            boxShadow: '0 2px 8px rgba(19, 43, 32, 0.15)'
          }}>
            <Shield size={22} color="#D49B44" />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: '#132B20' }}>
              Official Evidentiary Chain-of-Custody
            </h3>
            <div style={{ fontSize: '0.72rem', color: '#526058' }}>
              Human-in-the-Loop Verification Gate • Section 65B Audit
            </div>
          </div>
        </div>

        {/* Notice Info Box */}
        <div style={{
          backgroundColor: '#FCFCFA',
          borderRadius: '12px',
          padding: '16px',
          fontSize: '0.82rem',
          lineHeight: '1.5',
          color: '#1F2937',
          border: '1px solid #D4CEBF',
          marginBottom: '22px'
        }}>
          <p style={{ margin: '0 0 10px 0', color: '#8A5A18', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '6px' }}>
            ⚠️ Law Enforcement Verification Notice:
          </p>
          <ul style={{ margin: 0, paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px', color: '#526058' }}>
            <li>
              This audio transcript will be saved as structured Markdown (<code>.md</code>) in session <strong style={{ color: '#132B20' }}>`{sessionId}`</strong>.
            </li>
            <li>
              <strong style={{ color: '#132B20' }}>Strict Replacement Model:</strong> Confirming this statement will index it as the active audio evidence in DuckDB RAG and automatically replace any previous audio statements.
            </li>
            <li>
              The <strong style={{ color: '#132B20' }}>Document & Legal Agent</strong> will immediately cite this transcript during chatbot queries.
            </li>
          </ul>
        </div>

        {/* Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '12px' }}>
          <button
            disabled={isInjecting}
            onClick={onCancel}
            style={{
              backgroundColor: '#EFEBE2',
              border: '1px solid #D4CEBF',
              color: '#526058',
              borderRadius: '8px',
              padding: '10px 18px',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: isInjecting ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!isInjecting) e.currentTarget.style.backgroundColor = '#EDE7DA';
            }}
            onMouseLeave={(e) => {
              if (!isInjecting) e.currentTarget.style.backgroundColor = '#EFEBE2';
            }}
          >
            Cancel / Keep Staged
          </button>

          <button
            disabled={isInjecting}
            onClick={onConfirm}
            style={{
              backgroundColor: isInjecting ? '#A8A29E' : '#132B20',
              color: '#FCFCFA',
              border: '1px solid #132B20',
              borderRadius: '8px',
              padding: '10px 22px',
              fontSize: '0.86rem',
              fontWeight: 800,
              cursor: isInjecting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: isInjecting ? 'none' : '0 4px 14px rgba(19, 43, 32, 0.2)',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!isInjecting) {
                e.currentTarget.style.backgroundColor = '#0F5132';
                e.currentTarget.style.borderColor = '#D49B44';
              }
            }}
            onMouseLeave={(e) => {
              if (!isInjecting) {
                e.currentTarget.style.backgroundColor = '#132B20';
                e.currentTarget.style.borderColor = '#132B20';
              }
            }}
          >
            {isInjecting ? (
              <>Indexing Markdown into RAG...</>
            ) : (
              <>
                <CheckCircle2 size={16} color="#D49B44" /> Confirm & Inject Evidence
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
