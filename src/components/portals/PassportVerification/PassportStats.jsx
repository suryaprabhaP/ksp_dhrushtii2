import React from 'react';
import { ShieldCheck, Clock, AlertTriangle, CheckCircle, XCircle, Flame } from 'lucide-react';

export default function PassportStats({ records, activeTab, setActiveTab }) {
  const total = records.length;
  const pending = records.filter(r => r.status === 'PENDING' || r.status === 'FIELD_VISIT_DONE').length;
  const tatkal = records.filter(r => r.priority === 'TATKAL' && r.status === 'PENDING').length;
  const flagged = records.filter(r => r.status === 'FLAGGED' || r.criminal_record).length;
  const verified = records.filter(r => r.status === 'VERIFIED').length;
  const rejected = records.filter(r => r.status === 'REJECTED').length;

  const statCards = [
    { id: 'queue', label: 'Actionable Queue', count: pending, icon: Clock, color: '#132B20', activeBg: '#EFEBE2' },
    { id: 'tatkal', label: 'Tatkal Express', count: tatkal, icon: Flame, color: '#C88A2C', activeBg: 'rgba(212, 155, 68, 0.12)' },
    { id: 'flagged', label: 'Adverse / Flagged', count: flagged, icon: AlertTriangle, color: '#DC2626', activeBg: 'rgba(220, 38, 38, 0.08)' },
    { id: 'verified', label: 'Verified & Cleared', count: verified, icon: CheckCircle, color: '#0F5132', activeBg: 'rgba(15, 81, 50, 0.08)' },
    { id: 'rejected', label: 'Rejected', count: rejected, icon: XCircle, color: '#4B5563', activeBg: 'rgba(75, 85, 99, 0.08)' },
    { id: 'all', label: 'Total Dossiers', count: total, icon: ShieldCheck, color: '#132B20', activeBg: '#EFEBE2' }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '20px' }}>
      {statCards.map(c => {
        const Icon = c.icon;
        const isActive = activeTab === c.id;
        return (
          <div
            key={c.id}
            onClick={() => setActiveTab(c.id)}
            style={{
              background: isActive ? c.activeBg : '#FCFCFA',
              border: isActive ? `1.5px solid ${c.color}` : '1px solid #D4CEBF',
              borderRadius: '12px',
              padding: '14px 16px',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              transition: 'all 0.15s ease',
              boxShadow: isActive ? '0 4px 12px rgba(19, 43, 32, 0.08)' : '0 1px 3px rgba(19, 43, 32, 0.03)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#526058' }}>{c.label}</span>
              <Icon size={16} color={c.color} />
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: c.color }}>
              {c.count}
            </div>
          </div>
        );
      })}
    </div>
  );
}