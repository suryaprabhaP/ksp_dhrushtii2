import React from 'react';
import { User, Phone, MapPin, Shield } from 'lucide-react';
import { KARNATAKA_DISTRICTS_STATIONS } from './constants';

export default function ComplainantForm({ formData, updateField, onNext, onCancel }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.fullName || !formData.mobileNumber) {
      alert('Please enter your full name and mobile number.');
      return;
    }
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
          <User size={18} /> Step 1: Complainant Identity & Contact Details
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Full Name *
            </label>
            <input
              type="text"
              required
              value={formData.fullName}
              onChange={(e) => updateField('fullName', e.target.value)}
              placeholder="e.g. Ramesh Kumar"
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

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Mobile Number (10 digits) *
            </label>
            <input
              type="tel"
              required
              pattern="[0-9]{10}"
              value={formData.mobileNumber}
              onChange={(e) => updateField('mobileNumber', e.target.value)}
              placeholder="98XXXXXXXX"
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

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Email Address
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => updateField('email', e.target.value)}
              placeholder="ramesh@example.com"
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

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Gender
            </label>
            <select
              value={formData.gender}
              onChange={(e) => updateField('gender', e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '0.85rem'
              }}
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Transgender">Transgender</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              District
            </label>
            <select
              value={formData.district}
              onChange={(e) => updateField('district', e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '0.85rem'
              }}
            >
              {Object.keys(KARNATAKA_DISTRICTS_STATIONS).map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Present Address
            </label>
            <input
              type="text"
              value={formData.presentAddress}
              onChange={(e) => updateField('presentAddress', e.target.value)}
              placeholder="#12, 4th Cross, Indiranagar"
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
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: '10px 20px',
            background: 'transparent',
            border: '1px solid #475569',
            borderRadius: '8px',
            color: '#94a3b8',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Cancel
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
          Next: Incident Details →
        </button>
      </div>
    </form>
  );
}