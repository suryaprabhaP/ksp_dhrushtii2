import React from 'react';
import { X, Check, XCircle, AlertTriangle, ShieldCheck, Download } from 'lucide-react';
import { jsPDF } from 'jspdf';

export default function VerificationModal({ record, onClose, onApprove, onReject, onFlag }) {
  if (!record) return null;

  const downloadClearanceCertificate = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('KARNATAKA STATE POLICE — PASSPORT VERIFICATION REPORT', 20, 20);
    doc.setFontSize(10);
    doc.text(`Application ID: ${record.application_id}`, 20, 30);
    doc.text(`Applicant Name: ${record.applicant_name} (${record.gender})`, 20, 40);
    doc.text(`DOB: ${record.date_of_birth} | Aadhaar: ${record.aadhaar_number}`, 20, 50);
    doc.text(`Police Station: ${record.police_station} (${record.division})`, 20, 60);
    doc.text(`Verification Status: ${record.status}`, 20, 70);
    doc.text(`Officer Remarks: ${record.verification_remarks || 'Clear background report approved.'}`, 20, 80, { maxWidth: 170 });
    doc.save(`KSP_Passport_Clearance_${record.application_id}.pdf`);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      background: 'rgba(19, 43, 32, 0.45)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div
        className="portal-scroll"
        style={{
          width: '100%',
          maxWidth: '780px',
          maxHeight: '90vh',
          overflowY: 'auto',
          background: '#F4F0E8',
          border: '1px solid #D4CEBF',
          borderRadius: '16px',
          padding: '28px',
          color: '#132B20',
          boxShadow: '0 20px 45px rgba(19, 43, 32, 0.15)'
        }}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '20px',
          borderBottom: '1px solid #D4CEBF',
          paddingBottom: '16px'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#8A5A18', letterSpacing: '0.5px' }}>
              POLICE VERIFICATION DOSSIER
            </span>
            <h2 style={{ margin: '4px 0 0 0', fontSize: '1.3rem', fontWeight: 900, color: '#132B20' }}>
              {record.applicant_name} ({record.application_id})
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#FCFCFA',
              border: '1px solid #D4CEBF',
              borderRadius: '8px',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#132B20',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#EFEBE2'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FCFCFA'}
          >
            <X size={18} />
          </button>
        </div>

        {/* Info Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '14px',
          marginBottom: '20px',
          fontSize: '0.85rem'
        }}>
          <div style={{ background: '#FCFCFA', border: '1px solid #D4CEBF', padding: '12px 16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(19, 43, 32, 0.03)' }}>
            <span style={{ color: '#526058', display: 'block', fontSize: '0.7rem', fontWeight: 600, marginBottom: '2px' }}>Aadhaar Number</span>
            <strong style={{ color: '#132B20', fontSize: '0.9rem' }}>{record.aadhaar_number}</strong>
          </div>
          <div style={{ background: '#FCFCFA', border: '1px solid #D4CEBF', padding: '12px 16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(19, 43, 32, 0.03)' }}>
            <span style={{ color: '#526058', display: 'block', fontSize: '0.7rem', fontWeight: 600, marginBottom: '2px' }}>Jurisdiction</span>
            <strong style={{ color: '#132B20', fontSize: '0.9rem' }}>{record.police_station}</strong> <span style={{ color: '#526058', fontSize: '0.8rem' }}>({record.division})</span>
          </div>
          <div style={{ background: '#FCFCFA', border: '1px solid #D4CEBF', padding: '12px 16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(19, 43, 32, 0.03)' }}>
            <span style={{ color: '#526058', display: 'block', fontSize: '0.7rem', fontWeight: 600, marginBottom: '2px' }}>Purpose & Country</span>
            <strong style={{ color: '#132B20', fontSize: '0.9rem' }}>{record.purpose}</strong> <span style={{ color: '#8A5A18', fontSize: '0.8rem', fontWeight: 700 }}>({record.travel_country})</span>
          </div>
          <div style={{ background: '#FCFCFA', border: '1px solid #D4CEBF', padding: '12px 16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(19, 43, 32, 0.03)' }}>
            <span style={{ color: '#526058', display: 'block', fontSize: '0.7rem', fontWeight: 600, marginBottom: '2px' }}>Assigned Field Officer</span>
            <strong style={{ color: '#132B20', fontSize: '0.9rem' }}>{record.assigned_constable_name}</strong> <span style={{ color: '#6E7D75', fontSize: '0.8rem' }}>({record.assigned_constable_id})</span>
          </div>
        </div>

        {/* Remarks Box */}
        <div style={{
          background: '#FCFCFA',
          border: '1px solid #D4CEBF',
          borderRadius: '10px',
          padding: '16px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(19, 43, 32, 0.03)'
        }}>
          <span style={{ color: '#8A5A18', fontWeight: 800, fontSize: '0.75rem', display: 'block', marginBottom: '6px', letterSpacing: '0.3px' }}>
            OFFICER VERIFICATION REMARKS / CCTNS AUDIT:
          </span>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#132B20', lineHeight: 1.5, fontWeight: 500 }}>
            {record.verification_remarks || 'Physical verification conducted. Identity, address proof, and non-involvement in crime verified across CCTNS records.'}
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={downloadClearanceCertificate}
            style={{
              padding: '10px 16px',
              background: '#EFEBE2',
              border: '1px solid #D4CEBF',
              borderRadius: '8px',
              color: '#132B20',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#E5DEC9'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#EFEBE2'}
          >
            <Download size={15} /> Download Police Report PDF
          </button>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => onReject(record)}
              style={{
                padding: '10px 18px',
                background: 'rgba(220, 38, 38, 0.1)',
                border: '1px solid rgba(220, 38, 38, 0.3)',
                borderRadius: '8px',
                color: '#DC2626',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.18)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.1)'}
            >
              <XCircle size={15} /> Reject
            </button>
            <button
              onClick={() => onApprove(record)}
              style={{
                padding: '10px 22px',
                background: '#132B20',
                border: 'none',
                borderRadius: '8px',
                color: '#FCFCFA',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(19, 43, 32, 0.2)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1D3D2F'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#132B20'}
            >
              <Check size={16} /> Clear & Approve Verification
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}