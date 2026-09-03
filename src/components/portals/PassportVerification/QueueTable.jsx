import React from 'react';
import { Eye, Check, X, AlertTriangle, Clock } from 'lucide-react';

export default function QueueTable({ records, onSelectRecord, onApprove, onReject, onFlag }) {
  if (!records || records.length === 0) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#94a3b8', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '12px', border: '1px solid #334155' }}>
        No passport verification applications found for the selected criteria.
      </div>
    );
  }

  const getStatusBadge = (status, priority) => {
    if (priority === 'TATKAL' && status === 'PENDING') {
      return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#f59e0b22', color: '#fbbf24', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #f59e0b66' }}>⚡ TATKAL PENDING</span>;
    }
    switch (status) {
      case 'VERIFIED':
        return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#10b98122', color: '#34d399', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #10b98166' }}>✓ VERIFIED</span>;
      case 'REJECTED':
        return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#ef444422', color: '#f87171', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #ef444466' }}>✕ REJECTED</span>;
      case 'FLAGGED':
        return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#dc262622', color: '#fca5a5', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #dc262666' }}>⚠️ ADVERSE FLAGGED</span>;
      case 'FIELD_VISIT_DONE':
        return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#3b82f622', color: '#60a5fa', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #3b82f666' }}>VISIT DONE</span>;
      default:
        return <span style={{ padding: '3px 8px', borderRadius: '6px', background: '#64748b22', color: '#94a3b8', fontSize: '0.7rem', fontWeight: 800, border: '1px solid #64748b66' }}>PENDING</span>;
    }
  };

  return (
    <div style={{ overflowX: 'auto', background: 'rgba(15, 23, 42, 0.7)', borderRadius: '12px', border: '1px solid rgba(59, 130, 246, 0.25)' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem', color: '#f8fafc' }}>
        <thead>
          <tr style={{ background: 'rgba(30, 41, 59, 0.8)', borderBottom: '1px solid #334155', color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            <th style={{ padding: '12px 16px' }}>App ID / Applicant</th>
            <th style={{ padding: '12px 16px' }}>Jurisdiction</th>
            <th style={{ padding: '12px 16px' }}>Type & Travel</th>
            <th style={{ padding: '12px 16px' }}>Assigned Officer</th>
            <th style={{ padding: '12px 16px' }}>Status</th>
            <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r, idx) => (
            <tr
              key={r.application_id || idx}
              style={{
                borderBottom: '1px solid rgba(51, 65, 85, 0.5)',
                background: idx % 2 === 0 ? 'transparent' : 'rgba(30, 41, 59, 0.3)',
                transition: 'background 0.15s ease'
              }}
            >
              <td style={{ padding: '12px 16px' }}>
                <div style={{ fontWeight: 800, color: '#38bdf8' }}>{r.application_id}</div>
                <div style={{ fontSize: '0.85rem', color: '#f1f5f9' }}>{r.applicant_name}</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Aadhaar: {r.aadhaar_number}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#cbd5e1', fontWeight: 600 }}>{r.police_station}</div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{r.sub_division} • {r.division}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#e2e8f0' }}>{r.passport_type || 'Fresh'}</div>
                <div style={{ fontSize: '0.7rem', color: '#38bdf8' }}>{r.purpose || r.travel_country || 'General'}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#cbd5e1' }}>{r.assigned_constable_name || 'Unassigned'}</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{r.assigned_constable_id}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                {getStatusBadge(r.status, r.priority)}
              </td>
              <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px' }}>
                  <button
                    onClick={() => onSelectRecord(r)}
                    style={{
                      padding: '6px 10px',
                      background: 'rgba(59, 130, 246, 0.15)',
                      border: '1px solid rgba(59, 130, 246, 0.4)',
                      borderRadius: '6px',
                      color: '#60a5fa',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <Eye size={13} /> View
                  </button>

                  {r.status !== 'VERIFIED' && (
                    <button
                      onClick={() => onApprove(r)}
                      style={{
                        padding: '6px 10px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        border: '1px solid rgba(16, 185, 129, 0.4)',
                        borderRadius: '6px',
                        color: '#34d399',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <Check size={13} /> Approve
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}