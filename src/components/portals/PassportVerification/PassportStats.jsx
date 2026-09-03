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
    { id: 'queue', label: 'Actionable Queue', count: pending, icon: Clock, color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.1)' },
    { id: 'tatkal', label: 'Tatkal Express', count: tatkal, icon: Flame, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },
    { id: 'flagged', label: 'Adverse / Flagged', count: flagged, icon: AlertTriangle, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { id: 'verified', label: 'Verified & Cleared', count: verified, icon: CheckCircle, color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    { id: 'rejected', label: 'Rejected', count: rejected, icon: XCircle, color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.1)' },
    { id: 'all', label: 'Total Dossiers', count: total, icon: ShieldCheck, color: '#818cf8', bg: 'rgba(129, 140, 248, 0.1)' }
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
              background: isActive ? c.bg : 'rgba(15, 23, 42, 0.6)',
              border: isActive ? `1.5px solid ${c.color}` : '1px solid #334155',
              borderRadius: '12px',
              padding: '14px 16px',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              transition: 'all 0.2s ease',
              boxShadow: isActive ? `0 0 15px ${c.color}33` : 'none'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8' }}>{c.label}</span>
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