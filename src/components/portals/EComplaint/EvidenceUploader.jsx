import React from 'react';
import { Upload, Paperclip, CheckCircle2, Trash2 } from 'lucide-react';

export default function EvidenceUploader({ formData, updateField, onNext, onPrev }) {
  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      const fileNames = files.map(f => f.name);
      updateField('evidenceFiles', [...(formData.evidenceFiles || []), ...fileNames]);
    }
  };

  const removeFile = (idx) => {
    const newFiles = (formData.evidenceFiles || []).filter((_, i) => i !== idx);
    updateField('evidenceFiles', newFiles);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(59, 130, 246, 0.25)',
        borderRadius: '12px',
        padding: '20px',
        backdropFilter: 'blur(8px)'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1rem', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Upload size={18} /> Step 3: Suspect Details & Digital Evidence
        </h3>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
            Suspect Particulars (if known)
          </label>
          <input
            type="text"
            value={formData.suspectDetails}
            onChange={(e) => updateField('suspectDetails', e.target.value)}
            placeholder="e.g. Unknown male, approx 30 yrs old, wearing dark jacket, riding black Pulsar"
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '0.85rem'
            }}
          />
        </div>

        <div style={{
          border: '2px dashed rgba(59, 130, 246, 0.4)',
          borderRadius: '12px',
          padding: '24px',
          textAlign: 'center',
          background: 'rgba(30, 41, 59, 0.4)'
        }}>
          <Upload size={32} color="#60a5fa" style={{ margin: '0 auto 12px auto' }} />
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
            Upload Supporting Evidence Files
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '16px' }}>
            Attach CCTV clips, transaction screenshots, Aadhaar copy, or handwritten complaint scans (PNG, JPG, PDF, MP4)
          </div>
          
          <label style={{
            display: 'inline-block',
            padding: '8px 18px',
            background: 'rgba(59, 130, 246, 0.2)',
            border: '1px solid rgba(59, 130, 246, 0.5)',
            borderRadius: '8px',
            color: '#93c5fd',
            fontSize: '0.8rem',
            fontWeight: 800,
            cursor: 'pointer'
          }}>
            Browse Files
            <input type="file" multiple onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>

          {(formData.evidenceFiles || []).length > 0 && (
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8' }}>
                Attached Files ({(formData.evidenceFiles || []).length}):
              </div>
              {(formData.evidenceFiles || []).map((file, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'rgba(15, 23, 42, 0.8)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: '1px solid #334155'
                }}>
                  <span style={{ fontSize: '0.75rem', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Paperclip size={14} color="#60a5fa" /> {file}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
        <button
          type="button"
          onClick={onPrev}
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
          ← Back
        </button>
        <button
          type="submit"
          style={{
            padding: '10px 24px',
            background: 'linear-gradient(135deg, #1d4ed8, #2563eb)',
            border: 'none',
            borderRadius: '8px',
            color: '#ffffff',
            fontWeight: 800,
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)'
          }}
        >
          Review & Finalize →
        </button>
      </div>
    </div>
  );
}