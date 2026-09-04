import React from 'react';
import { Eye, Check, X, AlertTriangle, Clock } from 'lucide-react';

export default function QueueTable({ records, onSelectRecord, onApprove, onReject, onFlag }) {
  if (!records || records.length === 0) {
    return (
      <div style={{
        padding: '32px',
        textAlign: 'center',
        color: '#526058',
        background: '#FCFCFA',
        borderRadius: '12px',
        border: '1px solid #D4CEBF',
        boxShadow: '0 2px 8px rgba(19, 43, 32, 0.04)'
      }}>
        No passport verification applications found for the selected criteria.
      </div>
    );
  }

  const getStatusBadge = (status, priority) => {
    if (priority === 'TATKAL' && status === 'PENDING') {
      return (
        <span style={{
          padding: '3px 8px',
          borderRadius: '6px',
          background: 'rgba(212, 155, 68, 0.18)',
          color: '#8A5A18',
          fontSize: '0.7rem',
          fontWeight: 800,
          border: '1px solid #C88A2C'
        }}>
          ⚡ TATKAL PENDING
        </span>
      );
    }
    switch (status) {
      case 'VERIFIED':
        return (
          <span style={{
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(15, 81, 50, 0.12)',
            color: '#0F5132',
            fontSize: '0.7rem',
            fontWeight: 800,
            border: '1px solid rgba(15, 81, 50, 0.4)'
          }}>
            ✓ VERIFIED
          </span>
        );
      case 'REJECTED':
        return (
          <span style={{
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(220, 38, 38, 0.12)',
            color: '#DC2626',
            fontSize: '0.7rem',
            fontWeight: 800,
            border: '1px solid rgba(220, 38, 38, 0.3)'
          }}>
            ✕ REJECTED
          </span>
        );
      case 'FLAGGED':
        return (
          <span style={{
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(220, 38, 38, 0.15)',
            color: '#DC2626',
            fontSize: '0.7rem',
            fontWeight: 800,
            border: '1px solid #DC2626'
          }}>
            ⚠️ ADVERSE FLAGGED
          </span>
        );
      case 'FIELD_VISIT_DONE':
        return (
          <span style={{
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(212, 155, 68, 0.15)',
            color: '#976212',
            fontSize: '0.7rem',
            fontWeight: 800,
            border: '1px solid #C88A2C'
          }}>
            VISIT DONE
          </span>
        );
      default:
        return (
          <span style={{
            padding: '3px 8px',
            borderRadius: '6px',
            background: '#EFEBE2',
            color: '#526058',
            fontSize: '0.7rem',
            fontWeight: 800,
            border: '1px solid #D4CEBF'
          }}>
            PENDING
          </span>
        );
    }
  };

  return (
    <div
      className="portal-scroll"
      style={{
        overflowX: 'auto',
        background: '#FCFCFA',
        borderRadius: '12px',
        border: '1px solid #D4CEBF',
        boxShadow: '0 4px 15px rgba(19, 43, 32, 0.05)'
      }}
    >
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem', color: '#132B20' }}>
        <thead>
          <tr style={{
            background: '#EAE4D6',
            borderBottom: '1px solid #D4CEBF',
            color: '#132B20',
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            <th style={{ padding: '14px 16px', fontWeight: 800 }}>App ID / Applicant</th>
            <th style={{ padding: '14px 16px', fontWeight: 800 }}>Jurisdiction</th>
            <th style={{ padding: '14px 16px', fontWeight: 800 }}>Type & Travel</th>
            <th style={{ padding: '14px 16px', fontWeight: 800 }}>Assigned Officer</th>
            <th style={{ padding: '14px 16px', fontWeight: 800 }}>Status</th>
            <th style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 800 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r, idx) => (
            <tr
              key={r.application_id || idx}
              style={{
                borderBottom: '1px solid #EBE5DA',
                background: idx % 2 === 0 ? '#FCFCFA' : '#F9F7F2',
                transition: 'background 0.15s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1EDE4'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = idx % 2 === 0 ? '#FCFCFA' : '#F9F7F2'}
            >
              <td style={{ padding: '12px 16px' }}>
                <div style={{ fontWeight: 800, color: '#132B20' }}>{r.application_id}</div>
                <div style={{ fontSize: '0.85rem', color: '#132B20', fontWeight: 600 }}>{r.applicant_name}</div>
                <div style={{ fontSize: '0.72rem', color: '#6E7D75' }}>Aadhaar: {r.aadhaar_number}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#132B20', fontWeight: 600 }}>{r.police_station}</div>
                <div style={{ fontSize: '0.72rem', color: '#526058' }}>{r.sub_division} • {r.division}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#132B20', fontWeight: 600 }}>{r.passport_type || 'Fresh'}</div>
                <div style={{ fontSize: '0.72rem', color: '#8A5A18', fontWeight: 700 }}>{r.purpose || r.travel_country || 'General'}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <div style={{ color: '#132B20', fontWeight: 600 }}>{r.assigned_constable_name || 'Unassigned'}</div>
                <div style={{ fontSize: '0.72rem', color: '#6E7D75' }}>{r.assigned_constable_id}</div>
              </td>
              <td style={{ padding: '12px 16px' }}>
                {getStatusBadge(r.status, r.priority)}
              </td>
              <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button
                    onClick={() => onSelectRecord(r)}
                    style={{
                      padding: '6px 12px',
                      background: '#FCFCFA',
                      border: '1px solid #D4CEBF',
                      borderRadius: '6px',
                      color: '#132B20',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      transition: 'all 0.15s ease'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#EFEBE2'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FCFCFA'}
                  >
                    <Eye size={13} /> View
                  </button>

                  {r.status !== 'VERIFIED' && (
                    <button
                      onClick={() => onApprove(r)}
                      style={{
                        padding: '6px 12px',
                        background: '#132B20',
                        border: '1px solid #132B20',
                        borderRadius: '6px',
                        color: '#FCFCFA',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        boxShadow: '0 2px 6px rgba(19, 43, 32, 0.15)',
                        transition: 'all 0.15s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1D3D2F'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#132B20'}
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