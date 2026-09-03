import React, { useState } from 'react';
import { FileCheck, Download, CheckCircle2, Loader2, ArrowLeft } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { ComplaintAPI } from '../../../services/portalClient';

export default function ComplaintPreview({ formData, onSubmitted, onPrev }) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('KARNATAKA STATE POLICE — E-COMPLAINT RECEIPT', 20, 20);
    doc.setFontSize(10);
    doc.text(`Filing Date: ${new Date().toLocaleString()}`, 20, 30);
    doc.text(`Complainant: ${formData.fullName} (${formData.gender})`, 20, 40);
    doc.text(`Contact: ${formData.mobileNumber} | ${formData.email || 'N/A'}`, 20, 50);
    doc.text(`District: ${formData.incidentDistrict} | Station: ${formData.selectedStation}`, 20, 60);
    doc.text(`Crime Category: ${formData.natureOfComplaint}`, 20, 70);
    doc.text(`Incident Details:`, 20, 85);
    doc.text(formData.incidentDescription || 'None provided', 20, 95, { maxWidth: 170 });
    doc.text(`Attached Evidence: ${(formData.evidenceFiles || []).length} items`, 20, 140);
    doc.save(`KSP_EComplaint_${Date.now()}.pdf`);
  };

  const handleFinalSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        citizen_name: formData.fullName,
        phone: formData.mobileNumber,
        email: formData.email,
        station: formData.selectedStation,
        district: formData.incidentDistrict,
        division: formData.incidentDistrict.includes('Bengaluru') ? 'Bengaluru Division' : 'Karnataka State Range',
        category: formData.natureOfComplaint,
        description: formData.incidentDescription,
        suspect_details: formData.suspectDetails,
        incident_date: formData.incidentDate,
        evidence: formData.evidenceFiles || []
      };

      const res = await ComplaintAPI.submitComplaint(payload);
      if (res.success) {
        onSubmitted(res.acknowledgement_number || 'KSP-COMP-SUCCESS');
      } else {
        throw new Error(res.error || 'Filing failed');
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to submit complaint to Zoho Catalyst Data Store.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{
        background: 'rgba(15, 23, 42, 0.7)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '12px',
        padding: '24px',
        backdropFilter: 'blur(10px)'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileCheck size={20} /> Review E-Complaint Summary
        </h3>

        {error && (
          <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', fontSize: '0.85rem', marginBottom: '16px' }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '16px' }}>
          <div><strong style={{ color: '#94a3b8' }}>Complainant:</strong> {formData.fullName} ({formData.gender})</div>
          <div><strong style={{ color: '#94a3b8' }}>Mobile:</strong> {formData.mobileNumber}</div>
          <div><strong style={{ color: '#94a3b8' }}>Category:</strong> {formData.natureOfComplaint}</div>
          <div><strong style={{ color: '#94a3b8' }}>Station:</strong> {formData.selectedStation}</div>
          <div><strong style={{ color: '#94a3b8' }}>Incident Date:</strong> {formData.incidentDate}</div>
          <div><strong style={{ color: '#94a3b8' }}>Evidence Count:</strong> {(formData.evidenceFiles || []).length} file(s)</div>
        </div>

        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '14px', borderRadius: '8px', border: '1px solid #334155', marginBottom: '20px' }}>
          <strong style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '6px' }}>Statement / Narrative:</strong>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#f1f5f9', whiteSpace: 'pre-wrap' }}>
            {formData.incidentDescription}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={generatePDF}
            style={{
              padding: '10px 18px',
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
            <Download size={16} /> Download Draft PDF
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
        <button
          type="button"
          onClick={onPrev}
          disabled={submitting}
          style={{
            padding: '10px 20px',
            background: 'transparent',
            border: '1px solid #475569',
            borderRadius: '8px',
            color: '#cbd5e1',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          ← Edit Details
        </button>
        <button
          type="button"
          onClick={handleFinalSubmit}
          disabled={submitting}
          style={{
            padding: '12px 28px',
            background: 'linear-gradient(135deg, #10b981, #059669)',
            border: 'none',
            borderRadius: '8px',
            color: '#ffffff',
            fontWeight: 800,
            fontSize: '0.9rem',
            cursor: 'pointer',
            boxShadow: '0 4px 16px rgba(16, 185, 129, 0.4)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          {submitting ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}
          {submitting ? 'Registering in Catalyst...' : 'Confirm & Register Complaint'}
        </button>
      </div>
    </div>
  );
}