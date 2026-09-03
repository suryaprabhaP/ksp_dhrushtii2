import React from 'react';
import { AlertCircle, Calendar, MapPin } from 'lucide-react';
import { KARNATAKA_DISTRICTS_STATIONS, CRIME_CATEGORIES } from './constants';

export default function IncidentForm({ formData, updateField, onNext, onPrev }) {
  const stations = KARNATAKA_DISTRICTS_STATIONS[formData.incidentDistrict] || [];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.incidentDescription) {
      alert('Please provide a brief description of the incident.');
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
          <AlertCircle size={18} /> Step 2: Incident & Location Particulars
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Nature of Complaint / Crime Category *
            </label>
            <select
              value={formData.natureOfComplaint}
              onChange={(e) => updateField('natureOfComplaint', e.target.value)}
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
              {CRIME_CATEGORIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Incident District *
            </label>
            <select
              value={formData.incidentDistrict}
              onChange={(e) => {
                const newDist = e.target.value;
                updateField('incidentDistrict', newDist);
                const newStations = KARNATAKA_DISTRICTS_STATIONS[newDist] || [];
                if (newStations.length > 0) updateField('selectedStation', newStations[0]);
              }}
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
              Designated Police Station *
            </label>
            <select
              value={formData.selectedStation}
              onChange={(e) => updateField('selectedStation', e.target.value)}
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
              {stations.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
              Date & Time of Incident *
            </label>
            <input
              type="datetime-local"
              required
              value={formData.incidentDate}
              onChange={(e) => updateField('incidentDate', e.target.value)}
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

        <div style={{ marginTop: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
            Detailed Narrative of Incident *
          </label>
          <textarea
            required
            rows={4}
            value={formData.incidentDescription}
            onChange={(e) => updateField('incidentDescription', e.target.value)}
            placeholder="Provide a clear chronological statement of what occurred, involved entities, stolen items, or financial losses..."
            style={{
              width: '100%',
              padding: '12px 14px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '0.85rem',
              resize: 'vertical'
            }}
          />
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
          Next: Suspect & Evidence →
        </button>
      </div>
    </form>
  );
}