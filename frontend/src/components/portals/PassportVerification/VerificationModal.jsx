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
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '780px',
        maxHeight: '90vh',
        overflowY: 'auto',
        background: 'linear-gradient(145deg, #0f172a 0%, #1e293b 100%)',
        border: '1px solid rgba(59, 130, 246, 0.4)',
        borderRadius: '16px',
        padding: '24px',
        color: '#f8fafc',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid #334155', paddingBottom: '14px' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38bdf8', letterSpacing: '0.5px' }}>
              POLICE VERIFICATION DOSSIER
            </span>
            <h2 style={{ margin: '2px 0 0 0', fontSize: '1.25rem', fontWeight: 900 }}>
              {record.applicant_name} ({record.application_id})
            </h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Info Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '20px', fontSize: '0.85rem' }}>
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '10px 14px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', display: 'block', fontSize: '0.7rem' }}>Aadhaar Number</span>
            <strong>{record.aadhaar_number}</strong>
          </div>
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '10px 14px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', display: 'block', fontSize: '0.7rem' }}>Jurisdiction</span>
            <strong>{record.police_station}</strong> ({record.division})
          </div>
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '10px 14px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', display: 'block', fontSize: '0.7rem' }}>Purpose & Country</span>
            <strong>{record.purpose}</strong> ({record.travel_country})
          </div>
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '10px 14px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', display: 'block', fontSize: '0.7rem' }}>Assigned Field Officer</span>
            <strong>{record.assigned_constable_name}</strong> ({record.assigned_constable_id})
          </div>
        </div>

        {/* Remarks Box */}
        <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid #334155', borderRadius: '10px', padding: '14px', marginBottom: '24px' }}>
          <span style={{ color: '#60a5fa', fontWeight: 800, fontSize: '0.75rem', display: 'block', marginBottom: '4px' }}>
            OFFICER VERIFICATION REMARKS / CCTNS AUDIT:
          </span>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1' }}>
            {record.verification_remarks || 'Physical verification conducted. Identity, address proof, and non-involvement in crime verified across CCTNS records.'}
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={downloadClearanceCertificate}
            style={{
              padding: '10px 16px',
              background: 'rgba(59, 130, 246, 0.15)',
              border: '1px solid rgba(59, 130, 246, 0.4)',
              borderRadius: '8px',
              color: '#60a5fa',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Download size={15} /> Download Police Report PDF
          </button>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => onReject(record)}
              style={{
                padding: '10px 18px',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                borderRadius: '8px',
                color: '#f87171',
                fontSize: '0.85rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <XCircle size={15} /> Reject
            </button>
            <button
              onClick={() => onApprove(record)}
              style={{
                padding: '10px 22px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                fontSize: '0.85rem',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Check size={16} /> Clear & Approve Verification
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}