import React, { useState } from 'react';
import { ShieldAlert, ArrowLeft, CheckCircle2, Download, Loader2 } from 'lucide-react';
import { jsPDF } from 'jspdf';
import SpotDetailsForm from './SpotDetailsForm';
import SuspectSeizureForm from './SuspectSeizureForm';
import { PoliceFirAPI } from '../../../services/portalClient';

export default function PoliceInitiatedPortalContainer({ onBackToDashboard }) {
  const [step, setStep] = useState(1);
  const [caseId, setCaseId] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    officerBadge: 'KSP-88421',
    officerName: 'Inspector M. Venkatesh',
    officerRank: 'Police Inspector (PI)',
    incidentDistrict: 'Bengaluru Urban',
    policeStation: 'Bengaluru Urban Main PS',
    beatUnit: 'Night Patrol Beat #4',
    crimeCategory: 'Vehicle Theft / Spot Recovery',
    incidentDate: new Date().toISOString().slice(0, 10),
    spotLocation: '',
    spotNarrative: '',
    suspectStatus: 'APPREHENDED_ON_SPOT',
    suspectName: '',
    seizedItems: '',
    seizureValue: '0',
    panchaWitness: ''
  });

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFinalSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        officer_badge: formData.officerBadge,
        officer_name: formData.officerName,
        officer_rank: formData.officerRank,
        division: formData.incidentDistrict.includes('Bengaluru') ? 'Bengaluru Division' : 'State Range',
        sub_division: formData.incidentDistrict,
        police_station: formData.policeStation,
        beat_unit: formData.beatUnit,
        crime_category: formData.crimeCategory,
        incident_date: formData.incidentDate,
        spot_location: formData.spotLocation,
        spot_narrative: formData.spotNarrative,
        suspect_status: formData.suspectStatus,
        suspect_name: formData.suspectName,
        seized_items: formData.seizedItems,
        seizure_value: formData.seizureValue,
        pancha_witness: formData.panchaWitness
      };

      const res = await PoliceFirAPI.submitFir(payload);
      if (res.success) {
        setCaseId(res.record?.CaseId || `FIR-${Date.now()}`);
        setStep(3);
      } else {
        throw new Error(res.error || 'Failed to file FIR');
      }
    } catch (e) {
      console.error(e);
      setError(e.message || 'Zoho Catalyst DataStore insertion failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const downloadFIRDoc = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('KARNATAKA STATE POLICE — SUO-MOTO SPOT FIR', 20, 20);
    doc.setFontSize(10);
    doc.text(`FIR Date: ${new Date().toLocaleString()}`, 20, 30);
    doc.text(`Duty Officer: ${formData.officerName} (${formData.officerBadge})`, 20, 40);
    doc.text(`Station: ${formData.policeStation} | District: ${formData.incidentDistrict}`, 20, 50);
    doc.text(`Offense Category: ${formData.crimeCategory}`, 20, 60);
    doc.text(`Spot Location: ${formData.spotLocation}`, 20, 70);
    doc.text(`Suspect Details: ${formData.suspectName || 'Unknown'} (${formData.suspectStatus})`, 20, 80);
    doc.text(`Seized Articles (Panchanama): ${formData.seizedItems || 'None'} (Val: ₹${formData.seizureValue})`, 20, 90);
    doc.text(`Panchas: ${formData.panchaWitness || 'N/A'}`, 20, 100);
    doc.text(`Spot Narrative:`, 20, 115);
    doc.text(formData.spotNarrative || 'N/A', 20, 125, { maxWidth: 170 });
    doc.save(`KSP_SuoMoto_FIR_${Date.now()}.pdf`);
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      overflowY: 'auto',
      backgroundColor: '#090d16',
      color: '#f8fafc',
      padding: '24px 32px',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <button
          onClick={onBackToDashboard}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '8px',
            color: '#60a5fa',
            fontWeight: 700,
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          <ArrowLeft size={16} /> Back to Command Chatbot
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #ef4444, #b91c1c)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 10px rgba(239, 68, 68, 0.5)'
          }}>
            <ShieldAlert size={18} color="#ffffff" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 900, color: '#f8fafc' }}>
              Police-Initiated Suo-Moto FIR
            </h2>
            <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
              Patrol Interception & Seizure — Table 54626000000109574
            </span>
          </div>
        </div>
      </div>

      {step === 1 && (
        <SpotDetailsForm
          formData={formData}
          updateField={updateField}
          onNext={() => setStep(2)}
          onCancel={onBackToDashboard}
        />
      )}

      {step === 2 && (
        <SuspectSeizureForm
          formData={formData}
          updateField={updateField}
          onNext={() => setStep('review')}
          onPrev={() => setStep(1)}
        />
      )}

      {step === 'review' && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '12px',
          padding: '24px'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#60a5fa' }}>
            Review Suo-Moto Incident & Seizure Memo
          </h3>

          {error && (
            <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', fontSize: '0.85rem', marginBottom: '16px' }}>
              ⚠️ {error}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '16px' }}>
            <div><strong style={{ color: '#94a3b8' }}>Officer:</strong> {formData.officerName} ({formData.officerBadge})</div>
            <div><strong style={{ color: '#94a3b8' }}>Station:</strong> {formData.policeStation}</div>
            <div><strong style={{ color: '#94a3b8' }}>Offense:</strong> {formData.crimeCategory}</div>
            <div><strong style={{ color: '#94a3b8' }}>Spot:</strong> {formData.spotLocation}</div>
            <div><strong style={{ color: '#94a3b8' }}>Suspect:</strong> {formData.suspectName || 'Unknown'}</div>
            <div><strong style={{ color: '#94a3b8' }}>Seizure Value:</strong> ₹{formData.seizureValue}</div>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
            <button
              onClick={downloadFIRDoc}
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
              <Download size={16} /> Download Draft FIR
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
            <button
              type="button"
              onClick={() => setStep(2)}
              disabled={submitting}
              style={{ padding: '10px 20px', background: 'transparent', border: '1px solid #475569', borderRadius: '8px', color: '#cbd5e1', fontWeight: 700, cursor: 'pointer' }}
            >
              ← Edit Details
            </button>
            <button
              type="button"
              onClick={handleFinalSubmit}
              disabled={submitting}
              style={{
                padding: '12px 28px',
                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(239, 68, 68, 0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {submitting ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}
              {submitting ? 'Registering in Catalyst...' : 'Confirm & Log Suo-Moto FIR'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div style={{
          textAlign: 'center',
          padding: '48px 24px',
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: '16px',
          maxWidth: '560px',
          margin: '0 auto'
        }}>
          <CheckCircle2 size={56} color="#10b981" style={{ margin: '0 auto 16px auto' }} />
          <h2 style={{ margin: '0 0 8px 0', fontSize: '1.4rem', color: '#f8fafc' }}>
            Suo-Moto FIR Registered!
          </h2>
          <p style={{ margin: '0 0 20px 0', fontSize: '0.85rem', color: '#94a3b8' }}>
            Record saved to Table 54626000000109574.
          </p>
          <div style={{
            background: 'rgba(30, 41, 59, 0.8)',
            padding: '12px 20px',
            borderRadius: '10px',
            border: '1px solid #334155',
            fontSize: '1rem',
            fontWeight: 800,
            color: '#ef4444',
            marginBottom: '24px',
            letterSpacing: '1px'
          }}>
            CASE ID: {caseId}
          </div>
          <button
            onClick={onBackToDashboard}
            style={{
              padding: '12px 28px',
              background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 800,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            Return to Command Center
          </button>
        </div>
      )}
    </div>
  );
}