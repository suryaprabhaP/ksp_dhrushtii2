import React from 'react';
import { Shield, MapPin, Calendar, AlertCircle } from 'lucide-react';
import { KARNATAKA_DISTRICTS_STATIONS, POLICE_CRIME_CATEGORIES } from './constants';

export default function SpotDetailsForm({ formData, updateField, onNext, onCancel }) {
  const stations = KARNATAKA_DISTRICTS_STATIONS[formData.incidentDistrict] || [];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.spotLocation || !formData.spotNarrative) {
      alert('Please enter spot location and narrative.');
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
          <Shield size={18} /> Step 1: Officer Auth & Spot Details
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Duty Officer Badge ID *
            </label>
            <input
              type="text"
              required
              value={formData.officerBadge}
              onChange={(e) => updateField('officerBadge', e.target.value)}
              placeholder="e.g. KSP-88421"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Officer Full Name & Rank
            </label>
            <input
              type="text"
              value={formData.officerName}
              onChange={(e) => updateField('officerName', e.target.value)}
              placeholder="e.g. Inspector M. Venkatesh"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Patrol District
            </label>
            <select
              value={formData.incidentDistrict}
              onChange={(e) => {
                const newD = e.target.value;
                updateField('incidentDistrict', newD);
                const st = KARNATAKA_DISTRICTS_STATIONS[newD] || [];
                if (st.length > 0) updateField('policeStation', st[0]);
              }}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            >
              {Object.keys(KARNATAKA_DISTRICTS_STATIONS).map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Patrol Station Jurisdiction
            </label>
            <select
              value={formData.policeStation}
              onChange={(e) => updateField('policeStation', e.target.value)}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            >
              {stations.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Detected Crime Category *
            </label>
            <select
              value={formData.crimeCategory}
              onChange={(e) => updateField('crimeCategory', e.target.value)}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            >
              {POLICE_CRIME_CATEGORIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Spot Location / Landmark *
            </label>
            <input
              type="text"
              required
              value={formData.spotLocation}
              onChange={(e) => updateField('spotLocation', e.target.value)}
              placeholder="e.g. Near Silk Board Flyover Junction"
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }}
            />
          </div>
        </div>

        <div style={{ marginTop: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
            Officer Spot Observation & Discovery Narrative *
          </label>
          <textarea
            required
            rows={4}
            value={formData.spotNarrative}
            onChange={(e) => updateField('spotNarrative', e.target.value)}
            placeholder="Describe patrol observation, suspicious activity detected, vehicle intercept details, or spot interrogation summary..."
            style={{ width: '100%', padding: '12px 14px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem', resize: 'vertical' }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <button
          type="button"
          onClick={onCancel}
          style={{ padding: '10px 20px', background: 'transparent', border: '1px solid #475569', borderRadius: '8px', color: '#94a3b8', fontWeight: 700, cursor: 'pointer' }}
        >
          Cancel
        </button>
        <button
          type="submit"
          style={{ padding: '10px 24px', background: 'linear-gradient(135deg, #1d4ed8, #2563eb)', border: 'none', borderRadius: '8px', color: '#ffffff', fontWeight: 800, cursor: 'pointer' }}
        >
          Next: Suspect & Seizure →
        </button>
      </div>
    </form>
  );
}