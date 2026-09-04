import React, { useState, useEffect, useMemo } from 'react';
import { ArrowLeft, Search, Filter, ShieldCheck, Download, RefreshCw } from 'lucide-react';
import { getPassportRecords, savePassportRecords } from './passportDataset';
import PassportStats from './PassportStats';
import QueueTable from './QueueTable';
import VerificationModal from './VerificationModal';
import { PassportAPI } from '../../../services/portalClient';

export default function PassportPortalContainer({ onBackToDashboard }) {
  const [records, setRecords] = useState([]);
  const [activeTab, setActiveTab] = useState('queue');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load from API or fallback dataset
  const loadData = async () => {
    setLoading(true);
    try {
      const cloudRecords = await PassportAPI.getPassports();
      if (cloudRecords && cloudRecords.length > 0) {
        setRecords(cloudRecords);
      } else {
        const local = getPassportRecords();
        setRecords(local);
      }
    } catch (e) {
      console.warn('Using local fallback for passport dataset:', e);
      setRecords(getPassportRecords());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredRecords = useMemo(() => {
    return records.filter(r => {
      // Tab filter
      if (activeTab === 'queue' && (r.status !== 'PENDING' && r.status !== 'FIELD_VISIT_DONE')) return false;
      if (activeTab === 'tatkal' && (r.priority !== 'TATKAL' || r.status !== 'PENDING')) return false;
      if (activeTab === 'flagged' && (r.status !== 'FLAGGED' && !r.criminal_record)) return false;
      if (activeTab === 'verified' && r.status !== 'VERIFIED') return false;
      if (activeTab === 'rejected' && r.status !== 'REJECTED') return false;

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = (r.applicant_name || '').toLowerCase().includes(q);
        const matchId = (r.application_id || '').toLowerCase().includes(q);
        const matchStation = (r.police_station || '').toLowerCase().includes(q);
        if (!matchName && !matchId && !matchStation) return false;
      }
      return true;
    });
  }, [records, activeTab, searchQuery]);

  const handleApprove = async (rec) => {
    const updated = records.map(r => {
      if (r.application_id === rec.application_id) {
        return { ...r, status: 'VERIFIED', verification_remarks: 'Verification approved by Station House Officer.' };
      }
      return r;
    });
    setRecords(updated);
    savePassportRecords(updated);
    setSelectedRecord(null);

    // Sync to Catalyst Cloud
    try {
      if (rec.ROWID) {
        await PassportAPI.updateStatus(rec.ROWID, 'VERIFIED');
      }
    } catch (e) {}
  };

  const handleReject = async (rec) => {
    const updated = records.map(r => {
      if (r.application_id === rec.application_id) {
        return { ...r, status: 'REJECTED', verification_remarks: 'Adverse report filed by Investigating Officer.' };
      }
      return r;
    });
    setRecords(updated);
    savePassportRecords(updated);
    setSelectedRecord(null);

    try {
      if (rec.ROWID) {
        await PassportAPI.updateStatus(rec.ROWID, 'REJECTED');
      }
    } catch (e) {}
  };

  return (
    <div
      className="portal-scroll"
      style={{
        width: '100%',
        height: '100%',
        overflowY: 'auto',
        backgroundColor: '#F4F0E8',
        color: '#132B20',
        padding: '24px 32px',
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
      }}
    >
      {/* Top Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        background: '#FCFCFA',
        padding: '16px 20px',
        borderRadius: '12px',
        border: '1px solid #D4CEBF',
        boxShadow: '0 2px 8px rgba(19, 43, 32, 0.05)'
      }}>
        <button
          onClick={onBackToDashboard}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            background: '#EFEBE2',
            border: '1px solid #D4CEBF',
            borderRadius: '8px',
            color: '#132B20',
            fontWeight: 700,
            fontSize: '0.8rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
        >
          <ArrowLeft size={16} /> Back to Command Chatbot
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: '#132B20',
            border: '1px solid #D49B44',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(19, 43, 32, 0.15)'
          }}>
            <ShieldCheck size={20} color="#D49B44" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 900, color: '#132B20', letterSpacing: '-0.3px' }}>
              Passport Police Verification Portal
            </h2>
            <span style={{ fontSize: '0.72rem', color: '#526058', fontWeight: 600 }}>
              CCTNS Karnataka — Table 54626000000093001
            </span>
          </div>
        </div>
      </div>

      {/* Stats Ribbon */}
      <PassportStats records={records} activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Filter / Search Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          flex: 1,
          maxWidth: '420px',
          background: '#FCFCFA',
          border: '1px solid #D4CEBF',
          borderRadius: '8px',
          padding: '8px 14px',
          boxShadow: '0 1px 3px rgba(19, 43, 32, 0.04)'
        }}>
          <Search size={16} color="#7D8B82" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Applicant Name, App ID, Station..."
            style={{
              background: 'transparent',
              border: 'none',
              color: '#132B20',
              fontSize: '0.85rem',
              width: '100%',
              outline: 'none',
              fontWeight: 500
            }}
          />
        </div>

        <button
          onClick={loadData}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            background: '#EFEBE2',
            border: '1px solid #D4CEBF',
            borderRadius: '8px',
            color: '#132B20',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Table
        </button>
      </div>

      {/* Applications Table */}
      <QueueTable
        records={filteredRecords}
        onSelectRecord={(rec) => setSelectedRecord(rec)}
        onApprove={handleApprove}
        onReject={handleReject}
      />

      {/* Verification Details Modal */}
      {selectedRecord && (
        <VerificationModal
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
}