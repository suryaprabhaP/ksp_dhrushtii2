import React from 'react';
import { UserX, HardDrive, ShieldAlert, Paperclip } from 'lucide-react';

export default function SuspectSeizureForm({ formData, updateField, onNext, onPrev }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(59, 130, 246, 0.25)',
        borderRadius: '12px',
        padding: '20px',
        backdropFilter: 'blur(8px)'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1rem', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <UserX size={18} /> Step 2: Suspect Apprehension & Seizure Panchanama
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Suspect Status
            </label>
            <select
              value={formData.suspectStatus}
              onChange={(e) => updateField('suspectStatus', e.target.value)}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            >
              <option value="APPREHENDED_ON_SPOT">Apprehended on Spot</option>
              <option value="FLED_FROM_SCENE">Fled from Scene (Identified)</option>
              <option value="UNKNOWN_UNTRACEABLE">Unknown / Unidentified</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Suspect Full Name / Alias
            </label>
            <input
              type="text"
              value={formData.suspectName}
              onChange={(e) => updateField('suspectName', e.target.value)}
              placeholder="e.g. Manjunath alias 'Kulla' Manja"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Recovered / Seized Property
            </label>
            <input
              type="text"
              value={formData.seizedItems}
              onChange={(e) => updateField('seizedItems', e.target.value)}
              placeholder="e.g. Yamaha R15 (KA-05-EB-4192), 2 Smart Mobiles, ₹14,500 Cash"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Estimated Seizure Value (INR)
            </label>
            <input
              type="number"
              value={formData.seizureValue}
              onChange={(e) => updateField('seizureValue', e.target.value)}
              placeholder="e.g. 150000"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Independent Spot Witnesses (Panchas)
            </label>
            <input
              type="text"
              value={formData.panchaWitness}
              onChange={(e) => updateField('panchaWitness', e.target.value)}
              placeholder="e.g. 1. Syed Altaf (9845011111), 2. Vinay Kumar (9448022222)"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
        <button
          type="button"
          onClick={onPrev}
          style={{ padding: '10px 20px', background: 'transparent', border: '1px solid #475569', borderRadius: '8px', color: '#cbd5e1', fontWeight: 700, cursor: 'pointer' }}
        >
          ← Back
        </button>
        <button
          type="submit"
          style={{ padding: '10px 24px', background: 'linear-gradient(135deg, #1d4ed8, #2563eb)', border: 'none', borderRadius: '8px', color: '#ffffff', fontWeight: 800, cursor: 'pointer' }}
        >
          Next: Review & File Suo-Moto FIR →
        </button>
      </div>
    </form>
  );
}