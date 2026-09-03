import React from 'react';
import { Activity } from 'lucide-react';

export default function CommandCenterMenu({ onSelectView, onNavigateBackToCommandCenter }) {
  const handleClick = () => {
    if (onNavigateBackToCommandCenter) {
      onNavigateBackToCommandCenter();
    } else if (onSelectView) {
      onSelectView('main_command');
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onClick={handleClick}
        title="Return to KSP Main Command GIS Portal"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          border: '1px solid rgba(52, 211, 153, 0.4)',
          borderRadius: '8px',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '0.8rem',
          cursor: 'pointer',
          boxShadow: '0 0 15px rgba(16, 185, 129, 0.35)',
          letterSpacing: '0.3px',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-1px)';
          e.currentTarget.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.6)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 0 15px rgba(16, 185, 129, 0.35)';
        }}
      >
        <Activity size={15} color="#ffffff" />
        <span>COMMAND CENTER</span>
      </button>
    </div>
  );
}