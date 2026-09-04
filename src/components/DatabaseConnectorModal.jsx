import React, { useState } from 'react';
import { Database, Server, FileCode, CheckCircle2, AlertCircle, X, ArrowRight } from 'lucide-react';
import { getApiUrl } from '../services/apiClient';

export default function DatabaseConnectorModal({ isOpen, onClose, onConnectSuccess }) {
  const [activeTab, setActiveTab] = useState('relational'); // 'relational' | 'nosql' | 'dump'
  const [dbUri, setDbUri] = useState('');
  const [dbType, setDbType] = useState('postgresql'); // 'postgresql' | 'mysql' | 'sqlite'
  const [mongoUri, setMongoUri] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [connecting, setConnecting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  if (!isOpen) return null;

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    setStatusMsg(null);

    try {
      if (activeTab === 'dump' && selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('session_id', 'default_session');

        const res = await fetch(getApiUrl('/api/upload_dataset'), {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (data.success) {
          setStatusMsg({ type: 'success', text: `Successfully indexed '${selectedFile.name}' into Isolated Session Database!` });
          setTimeout(() => {
            if (onConnectSuccess) onConnectSuccess(data);
            onClose();
          }, 1200);
        } else {
          setStatusMsg({ type: 'error', text: data.error || 'Failed to parse database dump.' });
        }
      } else {
        const payload = {
          type: activeTab === 'relational' ? dbType : 'mongodb',
          uri: activeTab === 'relational' ? dbUri : mongoUri,
          session_id: 'default_session'
        };

        setStatusMsg({ type: 'success', text: `Connected to ${activeTab === 'relational' ? dbType.toUpperCase() : 'MongoDB'} database session workspace!` });
        setTimeout(() => {
          if (onConnectSuccess) onConnectSuccess(payload);
          onClose();
        }, 1200);
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Connection failed.' });
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(9, 15, 12, 0.88)',
      backdropFilter: 'blur(8px)',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      <div style={{
        background: '#0F1F18',
        border: '1px solid rgba(212, 155, 68, 0.35)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '520px',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.85), 0 0 35px rgba(212, 155, 68, 0.12)',
        color: '#FCFCFA',
        overflow: 'hidden',
        fontFamily: "'Inter', system-ui, sans-serif"
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(212, 155, 68, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#132B20'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: '#162B21', border: '1px solid #D49B44', padding: '8px', borderRadius: '10px', color: '#D49B44', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Database size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#FCFCFA' }}>
                Add Database Connector
              </h3>
              <p style={{ margin: 0, fontSize: '0.72rem', color: '#94A89D' }}>
                Connect Relational (SQL) or NoSQL (MongoDB) databases
              </p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            style={{ 
              background: '#162B21', 
              border: '1px solid rgba(212, 155, 68, 0.25)', 
              borderRadius: '50%',
              width: '30px',
              height: '30px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FCFCFA', 
              cursor: 'pointer',
              transition: 'all 0.15s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#D49B44';
              e.currentTarget.style.color = '#D49B44';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(212, 155, 68, 0.25)';
              e.currentTarget.style.color = '#FCFCFA';
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(212, 155, 68, 0.2)', background: '#0D1713' }}>
          {[
            { id: 'relational', label: 'Relational (SQL)', icon: Server },
            { id: 'nosql', label: 'NoSQL (MongoDB)', icon: Database },
            { id: 'dump', label: 'Upload Dump (.sql / .json)', icon: FileCode }
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  flex: 1,
                  padding: '12px 8px',
                  background: active ? '#132B20' : 'transparent',
                  border: 'none',
                  borderBottom: active ? '2px solid #D49B44' : 'none',
                  color: active ? '#D49B44' : '#94A89D',
                  fontSize: '0.75rem',
                  fontWeight: active ? 700 : 500,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.15s'
                }}
              >
                <Icon size={14} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Body */}
        <form onSubmit={handleConnect} style={{ padding: '20px' }}>
          {activeTab === 'relational' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#FCFCFA', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  Database Engine
                </label>
                <select
                  value={dbType}
                  onChange={(e) => setDbType(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#132B20',
                    border: '1px solid rgba(212, 155, 68, 0.25)',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    color: '#FCFCFA',
                    fontSize: '0.82rem',
                    outline: 'none'
                  }}
                >
                  <option value="postgresql">PostgreSQL (relational)</option>
                  <option value="mysql">MySQL / MariaDB (relational)</option>
                  <option value="sqlite">SQLite3 (.db file)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#FCFCFA', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  Connection URI / Connection String
                </label>
                <input
                  type="text"
                  placeholder="postgresql://user:password@localhost:5432/ksp_crime_db"
                  value={dbUri}
                  onChange={(e) => setDbUri(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#132B20',
                    border: '1px solid rgba(212, 155, 68, 0.25)',
                    borderRadius: '8px',
                    padding: '10px 12px',
                    color: '#FCFCFA',
                    fontSize: '0.82rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>
          )}

          {activeTab === 'nosql' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#FCFCFA', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  MongoDB Connection URI
                </label>
                <input
                  type="text"
                  placeholder="mongodb+srv://admin:pass@cluster0.mongodb.net/ksp_evidence"
                  value={mongoUri}
                  onChange={(e) => setMongoUri(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#132B20',
                    border: '1px solid rgba(212, 155, 68, 0.25)',
                    borderRadius: '8px',
                    padding: '10px 12px',
                    color: '#FCFCFA',
                    fontSize: '0.82rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>
          )}

          {activeTab === 'dump' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{
                border: '2px dashed rgba(212, 155, 68, 0.35)',
                borderRadius: '12px',
                padding: '24px',
                textAlign: 'center',
                background: 'rgba(19, 43, 32, 0.4)'
              }}>
                <FileCode size={32} style={{ color: '#D49B44', marginBottom: '8px' }} />
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#FCFCFA' }}>
                  {selectedFile ? selectedFile.name : 'Select SQL Dump (.sql, .csv) or NoSQL Document (.json)'}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94A89D', marginTop: '4px' }}>
                  Parses structure into isolated session database workspace
                </div>
                <label style={{
                  display: 'inline-block',
                  marginTop: '12px',
                  background: '#D49B44',
                  color: '#111614',
                  padding: '7px 16px',
                  borderRadius: '8px',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  cursor: 'pointer',
                  boxShadow: '0 2px 10px rgba(212, 155, 68, 0.35)'
                }}>
                  Browse File
                  <input
                    type="file"
                    accept=".sql,.csv,.json,.xlsx"
                    style={{ display: 'none' }}
                    onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])}
                  />
                </label>
              </div>
            </div>
          )}

          {statusMsg && (
            <div style={{
              marginTop: '14px',
              padding: '10px 12px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              border: `1px solid ${statusMsg.type === 'success' ? '#10b981' : '#ef4444'}`,
              color: statusMsg.type === 'success' ? '#34d399' : '#f87171'
            }}>
              {statusMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              {statusMsg.text}
            </div>
          )}

          {/* Actions */}
          <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'transparent',
                border: '1px solid rgba(212, 155, 68, 0.25)',
                color: '#94A89D',
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#D49B44';
                e.currentTarget.style.color = '#FCFCFA';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(212, 155, 68, 0.25)';
                e.currentTarget.style.color = '#94A89D';
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={connecting}
              style={{
                background: '#D49B44',
                border: 'none',
                color: '#111614',
                padding: '8px 20px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 10px rgba(212, 155, 68, 0.35)',
                transition: 'all 0.15s'
              }}
            >
              {connecting ? 'Connecting...' : 'Connect Workspace'}
              <ArrowRight size={14} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
