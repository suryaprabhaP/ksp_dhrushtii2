import React, { useState } from 'react';
import { ShieldCheck, ArrowLeft, CheckCircle2, FileText } from 'lucide-react';
import ComplainantForm from './ComplainantForm';
import IncidentForm from './IncidentForm';
import EvidenceUploader from './EvidenceUploader';
import ComplaintPreview from './ComplaintPreview';

export default function ComplaintPortalContainer({ onBackToDashboard }) {
  const [step, setStep] = useState(1);
  const [ackNumber, setAckNumber] = useState(null);
  
  const [formData, setFormData] = useState({
    fullName: '',
    mobileNumber: '',
    email: '',
    gender: 'Male',
    district: 'Bengaluru Urban',
    presentAddress: '',
    natureOfComplaint: 'Mobile Snatching / Theft',
    incidentDistrict: 'Bengaluru Urban',
    selectedStation: 'Bengaluru Urban Main PS',
    incidentDate: new Date().toISOString().slice(0, 16),
    incidentDescription: '',
    suspectDetails: '',
    evidenceFiles: []
  });

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmitted = (ack) => {
    setAckNumber(ack);
    setStep(5); // Success step
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
      {/* Top Breadcrumb Bar */}
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
            background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 10px rgba(37, 99, 235, 0.5)'
          }}>
            <ShieldCheck size={18} color="#ffffff" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 900, color: '#f8fafc' }}>
              Citizen E-Complaint Portal
            </h2>
            <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
              Karnataka State Police — Zoho Catalyst Cloud Ingestion
            </span>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      {step < 5 && (
        <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
          {['1. Complainant', '2. Incident Details', '3. Evidence Upload', '4. Review & Submit'].map((label, idx) => (
            <div
              key={idx}
              style={{
                flex: 1,
                padding: '10px 12px',
                borderRadius: '8px',
                background: step === idx + 1 ? 'rgba(59, 130, 246, 0.2)' : 'rgba(30, 41, 59, 0.4)',
                border: step === idx + 1 ? '1px solid #3b82f6' : '1px solid #334155',
                color: step === idx + 1 ? '#60a5fa' : '#64748b',
                fontWeight: 700,
                fontSize: '0.75rem',
                textAlign: 'center'
              }}
            >
              {label}
            </div>
          ))}
        </div>
      )}

      {/* Dynamic Step View */}
      {step === 1 && (
        <ComplainantForm
          formData={formData}
          updateField={updateField}
          onNext={() => setStep(2)}
          onCancel={onBackToDashboard}
        />
      )}

      {step === 2 && (
        <IncidentForm
          formData={formData}
          updateField={updateField}
          onNext={() => setStep(3)}
          onPrev={() => setStep(1)}
        />
      )}

      {step === 3 && (
        <EvidenceUploader
          formData={formData}
          updateField={updateField}
          onNext={() => setStep(4)}
          onPrev={() => setStep(2)}
        />
      )}

      {step === 4 && (
        <ComplaintPreview
          formData={formData}
          onSubmitted={handleSubmitted}
          onPrev={() => setStep(3)}
        />
      )}

      {step === 5 && (
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
            Complaint Successfully Lodged!
          </h2>
          <p style={{ margin: '0 0 20px 0', fontSize: '0.85rem', color: '#94a3b8' }}>
            Your official complaint has been written to the Zoho Catalyst Cloud DataStore.
          </p>
          <div style={{
            background: 'rgba(30, 41, 59, 0.8)',
            padding: '12px 20px',
            borderRadius: '10px',
            border: '1px solid #334155',
            fontSize: '1rem',
            fontWeight: 800,
            color: '#38bdf8',
            marginBottom: '24px',
            letterSpacing: '1px'
          }}>
            ACK NO: {ackNumber}
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