import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, FileText, CheckCircle2, ArrowRight, ArrowLeft, Upload, Check, Download, 
  AlertCircle, Phone, Lock, Calendar, MapPin, User, FilePlus, X, Eye, 
  Edit3, Camera, FileCheck, Paperclip, Plus, Minus, Image, Film, Smartphone, 
  Mic, FileCode, BadgeCheck, ShieldAlert, Radio, Search, Layers, RefreshCw, Zap
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import { pushPoliceCaseToCatalyst } from '../services/catalystPoliceService';
import { getPoliceComplaints, savePoliceComplaint } from '../dataset/police_complaint_catalyst_dataset';

const KARNATAKA_DISTRICTS_STATIONS = {
  'Bengaluru Urban': ['Bengaluru Urban Main PS', 'Indiranagar PS', 'Koramangala PS', 'Whitefield Cyber PS', 'Electronic City PS'],
  'Bengaluru Rural': ['Bengaluru Rural SP Office PS', 'Doddaballapura PS', 'Hosakote PS', 'Nelamangala PS'],
  'Chikkaballapura': ['Chikkaballapura Central PS', 'Gauribidanur PS', 'Chintamani PS', 'Bagepalli PS'],
  'Chitradurga': ['Chitradurga Town PS', 'Chitradurga Rural PS', 'Challakere PS', 'Hiriyur PS'],
  'Davanagere': ['Davanagere City PS', 'Harihar PS', 'Honnali PS', 'Channagiri PS'],
  'Kolar': ['Kolar Town PS', 'Mulbagal PS', 'Srinivaspur PS', 'Bangarapet PS'],
  'Kolar Gold Fields (KGF)': ['KGF Champion Reefs PS', 'Oorgaum PS', 'Marikuppam PS', 'Robertsonpet PS'],
  'Ramanagara': ['Ramanagara Town PS', 'Channapatna PS', 'Kanakapura PS', 'Magadi PS'],
  'Tumakuru': ['Tumakuru Town PS', 'Tiptur PS', 'Kunigal PS', 'Sira PS'],
  'Mysuru City': ['Mysuru Palace City PS', 'Vidyaranyapuram PS', 'Devaraja PS', 'Nazarbad PS'],
  'Mandya': ['Mandya Central PS', 'Maddur PS', 'Srirangapatna PS'],
  'Dakshina Kannada': ['Mangaluru North PS', 'Panambur Port PS', 'Bantwal PS'],
  'Belagavi District': ['Belagavi City PS', 'Gokak PS', 'Chikkodi PS'],
  'Kalaburagi District': ['Kalaburagi Central PS', 'Sedam PS', 'Shahabad PS']
};

/**
 * DRISHTI WARM PARCHMENT POLICE-INITIATED SUO MOTO FIR CONSOLE
 * Color Palette:
 * - Base Canvas: Warm Parchment (#F4F0E8 / #ECE6D9)
 * - Container Cards: Crisp Ivory (#FCFCFA)
 * - Borders: Warm Sand (#D4CEBF)
 * - Headings & Main Text: Tactical Forest Green (#132B20)
 * - Gold Accents & Highlights: Amber Gold (#D49B44)
 * - Secondary Text: Muted Charcoal (#526058)
 * - Secondary Fill: Soft Sand (#EFEBE2)
 */
function PoliceInitiatedComplaintPortal({ onClose, onBackToDashboard, onRegisterCase, initialStation = '', isModal = false }) {
  const [currentStep, setCurrentStep] = useState('welcome'); // welcome, step1, step2, step3, step4, step5, review, confirmation
  
  // Officer Authentication
  const [officerBadge, setOfficerBadge] = useState('KSP-88421');
  const [officerName, setOfficerName] = useState('Inspector M. Venkatesh');
  const [officerRank, setOfficerRank] = useState('Police Inspector (PI)');
  const [selectedStation, setSelectedStation] = useState(initialStation || 'Bengaluru Urban Main PS');
  const [incidentDistrict, setIncidentDistrict] = useState('Bengaluru Urban');
  const [beatUnit, setBeatUnit] = useState('Night Patrol Beat #4');

  // Step 2: Spot Incident Details
  const [crimeCategory, setCrimeCategory] = useState('Vehicle Theft / Spot Recovery');
  const [incidentDate, setIncidentDate] = useState(new Date().toISOString().split('T')[0]);
  const [incidentTime, setIncidentTime] = useState('02:15');
  const [spotLocation, setSpotLocation] = useState('');
  const [spotNarrative, setSpotNarrative] = useState('');

  // Step 3: Suspect / Accused Details
  const [suspectStatus, setSuspectStatus] = useState('Apprehended on Spot');
  const [suspectName, setSuspectName] = useState('');
  const [suspectAge, setSuspectAge] = useState('');
  const [suspectMarks, setSuspectMarks] = useState('');
  const [suspectAddress, setSuspectAddress] = useState('');

  // Witness Details
  const [witnessName, setWitnessName] = useState('');
  const [witnessContact, setWitnessContact] = useState('');

  // Step 4: Recovered Property / Seizure List
  const [propertySeized, setPropertySeized] = useState('Yes');
  const [seizureCategory, setSeizureCategory] = useState('Stolen Vehicle (Motorcycle)');
  const [seizureDescription, setSeizureDescription] = useState('');
  const [estimatedValue, setEstimatedValue] = useState('');
  const [seizureMemoNo, setSeizureMemoNo] = useState('PAN-2026/089');

  // Step 5: Upload Files & Officer Field Report
  const [officerReportFile, setOfficerReportFile] = useState('');
  const [uploadedEvidences, setUploadedEvidences] = useState([]);

  // Review & Submit State
  const [refNumber, setRefNumber] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [officerConsent, setOfficerConsent] = useState(false);

  const handleBack = () => {
    if (onBackToDashboard) {
      onBackToDashboard();
    } else if (onClose) {
      onClose();
    }
  };

  const handleDistrictChange = (dist) => {
    setIncidentDistrict(dist);
    const stations = KARNATAKA_DISTRICTS_STATIONS[dist] || [dist + ' Main PS'];
    setSelectedStation(stations[0]);
  };

  const handleQuickDemoStart = () => {
    setOfficerName('Inspector M. Venkatesh');
    setOfficerBadge('KSP-88421');
    setOfficerRank('Police Inspector (PI)');
    setSpotLocation('Near 100ft Road Junction, Koramangala 4th Block');
    setSpotNarrative('During night vehicle check, intercepted suspicious motorcycle without registration plate. Accused apprehended with break-in tools.');
    setSuspectName('Imran Pasha (24 yrs)');
    setSuspectAge('24');
    setSuspectMarks('Scar on left eyebrow');
    setSuspectAddress('Goripalya, Bengaluru');
    setSeizureDescription('1 KTM Duke Motorcycle (KA-01-ET-4491), 1 Master Lock-picking set');
    setEstimatedValue('2,10,000');
    setWitnessName('Santhosh M. (Security Guard)');
    setWitnessContact('9844011223');
    setCurrentStep('step1');
  };

  const handleOfficerReportUpload = (e) => {
    const file = e.target.files[0];
    if (file) setOfficerReportFile(file.name);
  };

  const handleEvidenceFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const newItems = files.map(f => ({
      id: Date.now() + Math.random().toString(36).substr(2, 4),
      name: f.name,
      size: (f.size / (1024 * 1024)).toFixed(2) + ' MB',
      type: f.type || 'Media File'
    }));
    setUploadedEvidences(prev => [...prev, ...newItems]);
  };

  const handleRemoveEvidence = (id) => {
    setUploadedEvidences(prev => prev.filter(item => item.id !== id));
  };

  // Submit Police-Initiated Case
  const handleSubmitPoliceCase = async () => {
    if (!officerConsent) {
      alert('Please check the Officer Verification Consent checkbox before submitting.');
      return;
    }

    setIsSubmitting(true);

    const generatedRef = `KSP-POL-2026-${Math.floor(10000 + Math.random() * 90000)}`;
    setRefNumber(generatedRef);

    const timestamp = new Date().toISOString();
    const formattedDate = new Date().toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    const caseRecord = {
      id: generatedRef,
      reference_number: generatedRef,
      type: 'POLICE_INITIATED_SUO_MOTO',
      status: 'REGISTERED SUO MOTO FIR / UNDER INVESTIGATION',
      filing_date: formattedDate,
      timestamp: timestamp,
      officer: {
        name: officerName,
        badge_id: officerBadge,
        rank: officerRank,
        police_station: selectedStation,
        district: incidentDistrict,
        beat_unit: beatUnit
      },
      incident: {
        nature: crimeCategory,
        date_from: incidentDate,
        time_from: incidentTime,
        location: spotLocation,
        description: spotNarrative,
        police_station: selectedStation,
        district: incidentDistrict
      },
      suspect: {
        known: true,
        status: suspectStatus,
        name: suspectName || 'Suspect Apprehended',
        approx_age: suspectAge,
        marks: suspectMarks,
        address: suspectAddress
      },
      witness: {
        witness_name: witnessName,
        contact: witnessContact
      },
      seizure: {
        property_seized: propertySeized === 'Yes',
        category: seizureCategory,
        description: seizureDescription,
        estimated_value: estimatedValue,
        memo_no: seizureMemoNo
      },
      evidence: {
        manual_report: officerReportFile || 'Logged Officer Entry',
        files: uploadedEvidences.map(e => e.name)
      },
      investigator: `${officerName} (${officerRank})`,
      section_laws: 'Sec 303/317 BNS, Sec 102 CrPC / Sec 105 BNSS (Seizure)'
    };

    // Save to localStorage
    try {
      const existingStr = localStorage.getItem('ksp_registered_complaints');
      const existing = existingStr ? JSON.parse(existingStr) : [];
      existing.unshift(caseRecord);
      localStorage.setItem('ksp_registered_complaints', JSON.stringify(existing));

      // Push to Catalyst Cloud DataStore
      await pushPoliceCaseToCatalyst({
        CaseId: caseRecord.id,
        OfficerBadge: caseRecord.officer?.badge_id || officerBadge,
        OfficerName: caseRecord.officer?.name || officerName,
        OfficerRank: caseRecord.officer?.rank || officerRank,
        Division: 'Bengaluru',
        SubDivision: caseRecord.officer?.district || incidentDistrict || 'Bengaluru Urban',
        PoliceStation: caseRecord.officer?.police_station || selectedStation || 'Central PS',
        BeatUnit: caseRecord.officer?.beat_unit || beatUnit || 'Beat Unit',
        CrimeCategory: caseRecord.incident?.nature || crimeCategory || 'Spot Operation',
        IncidentDate: `${caseRecord.incident?.date_from || ''} ${caseRecord.incident?.time_from || ''}`.trim(),
        SpotLocation: caseRecord.incident?.location || spotLocation || '',
        SpotNarrative: caseRecord.incident?.description || spotNarrative || '',
        SuspectStatus: caseRecord.suspect?.status || suspectStatus || 'Apprehended',
        SuspectName: caseRecord.suspect?.name || suspectName || 'Unknown Accused',
        SuspectDetails: `Age: ${caseRecord.suspect?.approx_age || suspectAge || 'N/A'}. Marks: ${caseRecord.suspect?.marks || suspectMarks || 'None'}. Address: ${caseRecord.suspect?.address || suspectAddress || 'N/A'}`,
        SeizedItems: caseRecord.seizure?.description || seizureDescription || 'No property listed',
        SeizureValue: `Rs. ${caseRecord.seizure?.estimated_value || estimatedValue || '0'}`,
        PanchaWitness: witnessName ? `${witnessName} (${witnessContact})` : 'Independent Witness',
        EvidenceCount: caseRecord.evidence?.files?.length || 2,
        EvidenceList: caseRecord.evidence?.files || ['Spot Seizure Memo', 'Inspection Photo'],
        CaseStatus: 'ACCUSED_IN_CUSTODY',
        FilingTimestamp: new Date().toISOString()
      });
    } catch (err) {
      console.error("Error saving to localStorage & Catalyst dataset:", err);
    }

    // Attach to global window database
    window.KSP_REGISTERED_COMPLAINTS = window.KSP_REGISTERED_COMPLAINTS || [];
    window.KSP_REGISTERED_COMPLAINTS.unshift(caseRecord);
    window.dispatchEvent(new CustomEvent('ksp_complaint_registered', { detail: caseRecord }));

    if (onRegisterCase) {
      onRegisterCase(caseRecord);
    }

    setIsSubmitting(false);
    setCurrentStep('confirmation');
  };

  // Download Police Seizure & FIR Report PDF
  const downloadPoliceReportPDF = () => {
    const doc = new jsPDF();
    const now = new Date().toLocaleString();

    doc.setDrawColor(19, 43, 32);
    doc.setLineWidth(1.5);
    doc.rect(8, 8, 194, 280);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.setTextColor(19, 43, 32);
    doc.text('KARNATAKA STATE POLICE', 105, 20, { align: 'center' });

    doc.setFontSize(10.5);
    doc.setTextColor(212, 155, 68);
    doc.text('POLICE-INITIATED SUO MOTO FIR & SEIZURE MEMO (BNSS SEC 105)', 105, 26, { align: 'center' });

    doc.setDrawColor(212, 206, 191);
    doc.setLineWidth(0.5);
    doc.line(15, 30, 195, 30);

    doc.setFillColor(244, 240, 232);
    doc.rect(15, 34, 180, 24, 'F');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11.5);
    doc.setTextColor(19, 43, 32);
    doc.text(`POLICE CASE REFERENCE ID: ${refNumber || 'KSP-POL-2026-48912'}`, 20, 44);
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(82, 96, 88);
    doc.text(`Patrol Officer: ${officerName} (${officerBadge}) | Station: ${selectedStation}`, 20, 52);

    let y = 68;

    const sections = [
      ['1. INVESTIGATING OFFICER & PATROL UNIT', [
        ['Officer Name:', officerName],
        ['Badge ID / Rank:', `${officerBadge} | ${officerRank}`],
        ['Police Station:', selectedStation],
        ['Patrol Beat Unit:', beatUnit]
      ]],
      ['2. SPOT INCIDENT DETAILS', [
        ['Offense Category:', crimeCategory],
        ['Date & Time Discovered:', `${incidentDate} at ${incidentTime}`],
        ['Spot Location:', spotLocation || 'Patrol Beat Sector 4'],
        ['Officer Observations:', spotNarrative || 'Offense observed during routine beat patrol. Action initiated on spot.']
      ]],
      ['3. ACCUSED / SUSPECT & WITNESS INFO', [
        ['Custody Status:', suspectStatus],
        ['Suspect Name:', suspectName || 'Suspect Apprehended'],
        ['Age & Marks:', `${suspectAge || 'N/A'} | Marks: ${suspectMarks || 'None'}`],
        ['Witness Name & Contact:', `${witnessName || 'Witness'} (${witnessContact || 'N/A'})`]
      ]],
      ['4. RECOVERED PROPERTY / SEIZURE MEMO', [
        ['Property Seized:', propertySeized],
        ['Seizure Category:', seizureCategory],
        ['Item Description:', seizureDescription || 'Property seized on spot under official memo'],
        ['Estimated Value:', `Rs. ${estimatedValue || '0'}`],
        ['Seizure Memo No:', seizureMemoNo]
      ]],
      ['5. EVIDENCE & OFFICER REPORT', [
        ['Officer Report File:', officerReportFile || 'Logged Officer Entry'],
        ['Evidence Attachments:', `${uploadedEvidences.length} Media File(s)`]
      ]]
    ];

    sections.forEach(([secTitle, fields]) => {
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.setTextColor(19, 43, 32);
      doc.text(secTitle, 15, y);
      y += 6;

      fields.forEach(([label, val]) => {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8.5);
        doc.setTextColor(82, 96, 88);
        doc.text(label, 20, y);

        doc.setFont('helvetica', 'normal');
        doc.setTextColor(19, 43, 32);
        const splitVal = doc.splitTextToSize(val, 125);
        doc.text(splitVal, 65, y);
        y += Math.max(5, splitVal.length * 4.5);
      });
      y += 4;
    });

    y += 6;
    doc.setFont('helvetica', 'italic');
    doc.setFontSize(7.5);
    doc.setTextColor(120);
    doc.text('Certified Official Police Record under BNSS Section 105 & Section 65B Evidence Act.', 15, y);

    doc.save(`Police_Case_Report_${refNumber || 'Receipt'}.pdf`);
  };

  const portalContent = (
    <div style={{
      width: '100%',
      height: isModal ? 'auto' : '100%',
      overflowY: 'auto',
      backgroundColor: '#F4F0E8',
      color: '#132B20',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    }}>
      {/* TOP HEADER BAR */}
      <div style={{
        background: '#FCFCFA',
        borderBottom: '1px solid #D4CEBF',
        padding: '14px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxShadow: '0 2px 8px rgba(19, 43, 32, 0.05)'
      }}>
        <button
          onClick={handleBack}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: '#EFEBE2',
            border: '1px solid #D4CEBF',
            borderRadius: '8px',
            color: '#132B20',
            fontWeight: 700,
            fontSize: '0.82rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={e => { e.currentTarget.style.background = '#E5DFD3'; }}
          onMouseLeave={e => { e.currentTarget.style.background = '#EFEBE2'; }}
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
            <ShieldAlert size={20} color="#D49B44" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 900, color: '#132B20', letterSpacing: '-0.3px' }}>
              Police-Initiated Suo-Moto FIR Portal
            </h2>
            <span style={{ fontSize: '0.72rem', color: '#526058', fontWeight: 600 }}>
              Karnataka State Police — BNSS Sec 105 Seizure & Spot Logging • Section 65B Certified
            </span>
          </div>
        </div>

        {isModal && (
          <button
            onClick={handleBack}
            style={{
              background: '#EFEBE2',
              border: '1px solid #D4CEBF',
              color: '#132B20',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* STEP PROGRESS INDICATOR */}
      {currentStep !== 'welcome' && currentStep !== 'confirmation' && (
        <div style={{
          background: '#FCFCFA',
          padding: '12px 28px',
          borderBottom: '1px solid #D4CEBF',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          flexWrap: 'wrap',
          zIndex: 40
        }}>
          {[
            { id: 'step1', label: '1. Officer Info' },
            { id: 'step2', label: '2. Spot Incident' },
            { id: 'step3', label: '3. Accused/Witness' },
            { id: 'step4', label: '4. Property Seizure' },
            { id: 'step5', label: '5. Evidence & Report' },
            { id: 'review', label: '6. Review & Submit' }
          ].map((s, i) => {
            const active = currentStep === s.id;
            const stepOrder = ['step1', 'step2', 'step3', 'step4', 'step5', 'review'];
            const currentNum = stepOrder.indexOf(currentStep) + 1;
            const thisNum = i + 1;
            const completed = thisNum < currentNum;

            return (
              <button
                key={s.id}
                onClick={() => setCurrentStep(s.id)}
                style={{
                  background: active ? '#132B20' : (completed ? '#EFEBE2' : '#EAE4D6'),
                  border: active ? '1px solid #D49B44' : (completed ? '1px solid #132B20' : '1px solid #D4CEBF'),
                  borderRadius: '10px',
                  padding: '8px 14px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  color: active ? '#D49B44' : (completed ? '#132B20' : '#526058'),
                  boxShadow: active ? '0 2px 8px rgba(19, 43, 32, 0.12)' : 'none',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  background: active ? '#D49B44' : (completed ? '#132B20' : '#D4CEBF'),
                  color: active ? '#132B20' : (completed ? '#D49B44' : '#526058'),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.68rem',
                  fontWeight: 900
                }}>
                  {completed ? <Check size={13} color="#D49B44" /> : thisNum}
                </div>
                <span>{s.label}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* MAIN BODY CONTAINER */}
      <div style={{
        flex: 1,
        padding: '24px 20px 48px 20px',
        maxWidth: '920px',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box'
      }}>

        {/* WELCOME / OFFICER AUTHENTICATION STEP */}
        {currentStep === 'welcome' && (
          <div style={{ textAlign: 'center', padding: '24px 12px' }}>
            <div style={{
              background: '#132B20',
              border: '1px solid #D49B44',
              color: '#D49B44',
              width: '68px',
              height: '68px',
              borderRadius: '20px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '18px',
              boxShadow: '0 10px 25px rgba(19, 43, 32, 0.15)'
            }}>
              <Radio size={34} />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 900, color: '#132B20', marginBottom: '8px' }}>
              Police-Initiated Suo Moto FIR Console
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#526058', maxWidth: '600px', margin: '0 auto 24px auto', lineHeight: 1.5 }}>
              Log criminal offenses discovered during beat patrol, spot seizures, raids, or routine checks, and generate official Suo Moto case files.
            </p>

            {/* OFFICER BADGE CARD */}
            <div style={{
              background: '#FCFCFA',
              padding: '28px',
              borderRadius: '20px',
              border: '1px solid #D4CEBF',
              maxWidth: '480px',
              margin: '0 auto',
              textAlign: 'left',
              boxShadow: '0 8px 24px rgba(19, 43, 32, 0.08)'
            }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#132B20', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BadgeCheck size={18} color="#D49B44" /> Officer Duty Authentication
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '16px' }}>
                <div>
                  <label style={labelStyle}>Officer Name:*</label>
                  <input type="text" value={officerName} onChange={e => setOfficerName(e.target.value)} style={lightInputStyle} />
                </div>
                <div>
                  <label style={labelStyle}>Badge / KGID No:*</label>
                  <input type="text" value={officerBadge} onChange={e => setOfficerBadge(e.target.value)} style={lightInputStyle} />
                </div>
                <div>
                  <label style={labelStyle}>Rank / Designation:*</label>
                  <select value={officerRank} onChange={e => setOfficerRank(e.target.value)} style={lightInputStyle}>
                    <option value="Police Inspector (PI)">Police Inspector (PI)</option>
                    <option value="Police Sub-Inspector (PSI)">Police Sub-Inspector (PSI)</option>
                    <option value="Assistant Sub-Inspector (ASI)">Assistant Sub-Inspector (ASI)</option>
                    <option value="Head Constable (HC)">Head Constable (HC)</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>District:*</label>
                  <select value={incidentDistrict} onChange={e => handleDistrictChange(e.target.value)} style={lightInputStyle}>
                    {Object.keys(KARNATAKA_DISTRICTS_STATIONS).map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={labelStyle}>Assigned Police Station:*</label>
                  <select value={selectedStation} onChange={e => setSelectedStation(e.target.value)} style={lightInputStyle}>
                    {(KARNATAKA_DISTRICTS_STATIONS[incidentDistrict] || ['Main Police Station']).map(ps => (
                      <option key={ps} value={ps}>{ps}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={() => setCurrentStep('step1')}
                style={{
                  width: '100%',
                  background: '#132B20',
                  color: '#D49B44',
                  border: '1px solid #D49B44',
                  padding: '12px',
                  borderRadius: '12px',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 14px rgba(19, 43, 32, 0.15)',
                  marginBottom: '10px'
                }}
              >
                <span>Authenticate & Open Suo Moto Entry Form</span>
                <ArrowRight size={16} />
              </button>

              <button
                onClick={handleQuickDemoStart}
                style={{
                  width: '100%',
                  background: '#EFEBE2',
                  color: '#132B20',
                  border: '1px solid #D4CEBF',
                  padding: '9px',
                  borderRadius: '10px',
                  fontWeight: 700,
                  fontSize: '0.76rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                ⚡ Quick Start (Demo Mode Pre-fill)
              </button>
            </div>
          </div>
        )}

        {/* STEP 1: OFFICER & PATROL DETAILS */}
        {currentStep === 'step1' && (
          <div style={stepCardStyle}>
            <h4 style={stepTitleStyle}>
              <BadgeCheck size={18} color="#D49B44" /> Step 1: Officer & Patrol Unit Information
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px', marginBottom: '16px' }}>
              <div>
                <label style={labelStyle}>Reporting Officer Name:*</label>
                <input type="text" value={officerName} onChange={e => setOfficerName(e.target.value)} style={lightInputStyle} />
              </div>
              <div>
                <label style={labelStyle}>Badge / KGID ID:*</label>
                <input type="text" value={officerBadge} onChange={e => setOfficerBadge(e.target.value)} style={lightInputStyle} />
              </div>
              <div>
                <label style={labelStyle}>Rank / Designation:*</label>
                <input type="text" value={officerRank} onChange={e => setOfficerRank(e.target.value)} style={lightInputStyle} />
              </div>
              <div>
                <label style={labelStyle}>Beat Patrol Unit / Sector:*</label>
                <input type="text" value={beatUnit} onChange={e => setBeatUnit(e.target.value)} style={lightInputStyle} />
              </div>
              <div>
                <label style={labelStyle}>District Jurisdiction:*</label>
                <input type="text" value={incidentDistrict} readOnly style={{ ...lightInputStyle, background: '#EFEBE2' }} />
              </div>
              <div>
                <label style={labelStyle}>Assigned Police Station:*</label>
                <input type="text" value={selectedStation} readOnly style={{ ...lightInputStyle, background: '#EFEBE2' }} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button onClick={() => setCurrentStep('step2')} style={btnPrimaryLight}>
                <span>Proceed to Spot Incident Details</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: SPOT INCIDENT DETAILS */}
        {currentStep === 'step2' && (
          <div style={stepCardStyle}>
            <h4 style={stepTitleStyle}>
              <MapPin size={18} color="#D49B44" /> Step 2: Spot Incident & Patrol Discovery Details
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px', marginBottom: '16px' }}>
              <div style={{ gridColumn: 'span 2' }}>
                <label style={labelStyle}>Offense Category / Discovered Incident:*</label>
                <select value={crimeCategory} onChange={e => setCrimeCategory(e.target.value)} style={lightInputStyle}>
                  <option value="Vehicle Theft / Spot Recovery">Vehicle Theft / Spot Recovery</option>
                  <option value="Illegal Narcotics / Contraband Possession">Illegal Narcotics / Contraband Possession</option>
                  <option value="Illegal Arms / Ammunition Seizure">Illegal Arms / Ammunition Seizure</option>
                  <option value="Extortion / Spot Robbery in Progress">Extortion / Spot Robbery in Progress</option>
                  <option value="Illegal Gambling Raid">Illegal Gambling Raid</option>
                  <option value="Physical Assault / Public Brawl">Physical Assault / Public Brawl</option>
                  <option value="Cyber Scam Hub Raid">Cyber Scam Hub Raid</option>
                  <option value="Liquor Bootlegging / Excise Violation">Liquor Bootlegging / Excise Violation</option>
                  <option value="Other Suo Moto Patrol Offense">Other Suo Moto Patrol Offense</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Discovery Date:*</label>
                <input type="date" value={incidentDate} onChange={e => setIncidentDate(e.target.value)} style={lightInputStyle} />
              </div>

              <div>
                <label style={labelStyle}>Discovery Time:*</label>
                <input type="time" value={incidentTime} onChange={e => setIncidentTime(e.target.value)} style={lightInputStyle} />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={labelStyle}>Exact Spot Location / GPS Landmark:*</label>
                <input type="text" placeholder="e.g. Near Outer Ring Road Junction, Beat Spot #4, Bengaluru" value={spotLocation} onChange={e => setSpotLocation(e.target.value)} style={lightInputStyle} />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={labelStyle}>Officer's Spot Observations & Narrative:*</label>
                <textarea rows={4} placeholder="Describe how the offense was spotted on patrol, officer actions taken, scene conditions..." value={spotNarrative} onChange={e => setSpotNarrative(e.target.value)} style={lightInputStyle} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
              <button onClick={() => setCurrentStep('step1')} style={btnSecondaryLight}><ArrowLeft size={16} /> Back</button>
              <button onClick={() => setCurrentStep('step3')} style={btnPrimaryLight}>
                <span>Proceed to Accused & Witness Details</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: ACCUSED / SUSPECT & WITNESS DETAILS */}
        {currentStep === 'step3' && (
          <div style={stepCardStyle}>
            <h4 style={stepTitleStyle}>
              <User size={18} color="#D49B44" /> Step 3: Person / Accused & Witness Details
            </h4>

            <div style={{ marginBottom: '18px', padding: '16px', background: '#EFEBE2', borderRadius: '12px', border: '1px solid #D4CEBF' }}>
              <label style={{ ...labelStyle, fontSize: '0.82rem', color: '#132B20', marginBottom: '8px' }}>Custody / Suspect Status:</label>
              <select value={suspectStatus} onChange={e => setSuspectStatus(e.target.value)} style={{ ...lightInputStyle, marginBottom: '12px' }}>
                <option value="Apprehended on Spot">Apprehended on Spot (In Police Custody)</option>
                <option value="Escaped / Fled Scene">Escaped / Fled Scene (Under Pursuit)</option>
                <option value="Questioned & Detained">Questioned & Detained</option>
                <option value="Unknown Offender">Unknown Offender</option>
              </select>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div>
                  <label style={labelStyle}>Accused Name / Alias:</label>
                  <input type="text" placeholder="e.g. Manikandan alias 'Chotta'" value={suspectName} onChange={e => setSuspectName(e.target.value)} style={lightInputStyle} />
                </div>
                <div>
                  <label style={labelStyle}>Approximate Age:</label>
                  <input type="text" placeholder="e.g. 28 years" value={suspectAge} onChange={e => setSuspectAge(e.target.value)} style={lightInputStyle} />
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={labelStyle}>Physical Identification Marks / Tattoos / Outfit:</label>
                  <input type="text" placeholder="e.g. Tattoo on right forearm, black jacket..." value={suspectMarks} onChange={e => setSuspectMarks(e.target.value)} style={lightInputStyle} />
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={labelStyle}>Accused Address / Native Place:</label>
                  <input type="text" placeholder="Address..." value={suspectAddress} onChange={e => setSuspectAddress(e.target.value)} style={lightInputStyle} />
                </div>
              </div>
            </div>

            {/* WITNESS INFO */}
            <div style={{ padding: '16px', background: '#EFEBE2', borderRadius: '12px', border: '1px solid #D4CEBF' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#132B20', marginBottom: '8px' }}>Eyewitness / Spot Witness Details:</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div>
                  <label style={labelStyle}>Witness #1 Name:</label>
                  <input type="text" placeholder="Full Name" value={witnessName} onChange={e => setWitnessName(e.target.value)} style={lightInputStyle} />
                </div>
                <div>
                  <label style={labelStyle}>Witness Mobile Contact:</label>
                  <input type="text" placeholder="e.g. 9844011223" value={witnessContact} onChange={e => setWitnessContact(e.target.value)} style={lightInputStyle} />
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
              <button onClick={() => setCurrentStep('step2')} style={btnSecondaryLight}><ArrowLeft size={16} /> Back</button>
              <button onClick={() => setCurrentStep('step4')} style={btnPrimaryLight}>
                <span>Proceed to Property Seizure</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: RECOVERED PROPERTY / SEIZURE LIST */}
        {currentStep === 'step4' && (
          <div style={stepCardStyle}>
            <h4 style={stepTitleStyle}>
              <Layers size={18} color="#D49B44" /> Step 4: Recovered Property & Seizure List (Panchanama)
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px', marginBottom: '16px' }}>
              <div>
                <label style={labelStyle}>Property Seized on Spot?</label>
                <select value={propertySeized} onChange={e => setPropertySeized(e.target.value)} style={lightInputStyle}>
                  <option value="Yes">Yes, Property / Contraband Seized</option>
                  <option value="No">No Property Seized</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Seizure Category:*</label>
                <select value={seizureCategory} onChange={e => setSeizureCategory(e.target.value)} style={lightInputStyle}>
                  <option value="Stolen Vehicle (Motorcycle)">Stolen Vehicle (Motorcycle)</option>
                  <option value="Stolen Vehicle (Car/Auto)">Stolen Vehicle (Car/Auto)</option>
                  <option value="Illegal Narcotics / Ganja / Drugs">Illegal Narcotics / Ganja / Drugs</option>
                  <option value="Illegal Firearms / Weapons">Illegal Firearms / Weapons</option>
                  <option value="Cash / Currency Notes">Cash / Currency Notes</option>
                  <option value="Mobile Phones / SIM Cards">Mobile Phones / SIM Cards</option>
                  <option value="Gambling Equipment / Cash">Gambling Equipment / Cash</option>
                  <option value="Other Seized Property">Other Seized Property</option>
                </select>
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={labelStyle}>Property Description / Chassis No / Make & Model:*</label>
                <textarea rows={2} placeholder="e.g. Pulsar 220 Bike KA-01-EF-9981, engine serial, color..." value={seizureDescription} onChange={e => setSeizureDescription(e.target.value)} style={lightInputStyle} />
              </div>

              <div>
                <label style={labelStyle}>Estimated Seizure Value (Rs.):</label>
                <input type="text" placeholder="e.g. 95,000" value={estimatedValue} onChange={e => setEstimatedValue(e.target.value)} style={lightInputStyle} />
              </div>

              <div>
                <label style={labelStyle}>Seizure Memo / Reference No:*</label>
                <input type="text" value={seizureMemoNo} onChange={e => setSeizureMemoNo(e.target.value)} style={lightInputStyle} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
              <button onClick={() => setCurrentStep('step3')} style={btnSecondaryLight}><ArrowLeft size={16} /> Back</button>
              <button onClick={() => setCurrentStep('step5')} style={btnPrimaryLight}>
                <span>Proceed to Evidence & Report Upload</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: EVIDENCE & OFFICER'S MANUAL REPORT UPLOAD */}
        {currentStep === 'step5' && (
          <div style={stepCardStyle}>
            <h4 style={stepTitleStyle}>
              <Upload size={18} color="#D49B44" /> Step 5: Upload Evidence & Officer Field Report
            </h4>

            {/* OFFICER MANUAL FIELD REPORT UPLOAD */}
            <div style={{ background: '#EFEBE2', border: '1px solid #D4CEBF', borderRadius: '16px', padding: '18px', marginBottom: '20px' }}>
              <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#132B20', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="#D49B44" /> Upload Officer's Manual Field Report / Daily Diary Scan
              </div>
              <p style={{ fontSize: '0.74rem', color: '#526058', margin: '0 0 12px 0' }}>
                Upload a scanned copy or photo of the officer's handwritten notebook entry, Daily Diary memo, or signed Seizure / Witness Memo sheet.
              </p>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                <label style={{ background: '#132B20', color: '#D49B44', border: '1px solid #D49B44', padding: '9px 16px', borderRadius: '10px', fontSize: '0.78rem', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Upload size={14} /> Upload Officer Report File
                  <input type="file" accept="image/*,.pdf" onChange={handleOfficerReportUpload} style={{ display: 'none' }} />
                </label>

                {officerReportFile ? (
                  <div style={{ fontSize: '0.78rem', color: '#132B20', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', background: '#FCFCFA', padding: '6px 12px', borderRadius: '8px', border: '1px solid #D49B44' }}>
                    <FileCheck size={16} color="#D49B44" /> Attached: {officerReportFile}
                  </div>
                ) : (
                  <span style={{ fontSize: '0.72rem', color: '#526058' }}>No officer report file uploaded</span>
                )}
              </div>
            </div>

            {/* MEDIA EVIDENCE UPLOAD */}
            <div style={{ background: '#FCFCFA', borderRadius: '16px', border: '1px solid #D4CEBF', padding: '18px', marginBottom: '20px' }}>
              <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#132B20', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Camera size={18} color="#D49B44" /> Spot Media Evidence (Photos, Videos/CCTV, Seizure Docs)
              </div>

              <label style={{ background: '#EFEBE2', border: '1.5px dashed #D49B44', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', marginBottom: '12px' }}>
                <Upload size={22} color="#D49B44" style={{ marginBottom: '4px' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#132B20' }}>Click to Browse Media & Evidence Files</span>
                <span style={{ fontSize: '0.68rem', color: '#526058' }}>Upload spot photos, CCTV clips, recovered item pictures</span>
                <input type="file" multiple onChange={handleEvidenceFileUpload} style={{ display: 'none' }} />
              </label>

              {uploadedEvidences.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {uploadedEvidences.map(file => (
                    <div key={file.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#EFEBE2', padding: '8px 12px', borderRadius: '8px', border: '1px solid #D4CEBF', fontSize: '0.74rem' }}>
                      <span style={{ color: '#132B20', fontWeight: 600 }}>📄 {file.name} ({file.size})</span>
                      <button onClick={() => handleRemoveEvidence(file.id)} style={{ background: 'transparent', border: 'none', color: '#8A5A18', cursor: 'pointer' }}><X size={14} /></button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
              <button onClick={() => setCurrentStep('step4')} style={btnSecondaryLight}><ArrowLeft size={16} /> Back</button>
              <button onClick={() => setCurrentStep('review')} style={btnPrimaryLight}>
                <span>Proceed to Final Verification</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 6: REVIEW & VERIFY PAGE */}
        {currentStep === 'review' && (
          <div style={stepCardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '2px solid #EAE4D6', paddingBottom: '10px' }}>
              <h4 style={{ ...stepTitleStyle, margin: 0, border: 'none', padding: 0 }}>
                <Eye size={18} color="#D49B44" /> Step 6: Officer Verification & Suo Moto FIR Review
              </h4>
              <button onClick={() => setCurrentStep('step1')} style={{ ...btnSecondaryLight, padding: '6px 12px', fontSize: '0.76rem', color: '#132B20', borderColor: '#D49B44' }}>
                <Edit3 size={14} color="#D49B44" /> Edit Case Form
              </button>
            </div>

            {/* REVIEW SUMMARY CARD */}
            <div style={{ background: '#EFEBE2', padding: '18px', borderRadius: '16px', border: '1px solid #D4CEBF', fontSize: '0.8rem', marginBottom: '18px', maxHeight: '320px', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', borderBottom: '1px solid #D4CEBF', paddingBottom: '8px' }}>
                <span style={{ fontWeight: 800, color: '#132B20' }}>🚔 Reporting Officer & Station:</span>
                <span style={{ color: '#8A5A18', fontWeight: 800 }}>{officerName} ({officerBadge}) — {selectedStation}</span>
              </div>

              <div style={{ fontWeight: 800, color: '#132B20', marginBottom: '6px' }}>📍 Spot Incident Details:</div>
              <div style={{ color: '#132B20', marginBottom: '12px', lineHeight: 1.6 }}>
                <b>Offense Category:</b> {crimeCategory}<br />
                <b>Date & Time:</b> {incidentDate} at {incidentTime}<br />
                <b>Spot Location:</b> {spotLocation}<br />
                <b>Observations:</b> "{spotNarrative}"
              </div>

              <div style={{ fontWeight: 800, color: '#132B20', marginBottom: '6px' }}>👤 Accused & Seizure Details:</div>
              <div style={{ color: '#132B20', marginBottom: '12px', lineHeight: 1.6 }}>
                <b>Accused Custody:</b> {suspectStatus} ({suspectName || 'Unidentified'})<br />
                <b>Property Seized:</b> {seizureCategory} (Rs. {estimatedValue || '0'}) — Memo: {seizureMemoNo}<br />
                <b>Witness:</b> {witnessName ? `${witnessName} (${witnessContact || 'No contact'})` : 'None recorded'}
              </div>

              <div style={{ fontWeight: 800, color: '#132B20', marginBottom: '6px' }}>📁 Officer Field Report & Attachments:</div>
              <div style={{ color: '#132B20', lineHeight: 1.6 }}>
                <b>Officer Report:</b> {officerReportFile || 'Logged'}<br />
                <b>Media Files:</b> {uploadedEvidences.map(f => f.name).join(', ') || 'None attached'}
              </div>
            </div>

            {/* OFFICER CONSENT CHECKBOX */}
            <div style={{ background: 'rgba(212, 155, 68, 0.12)', border: '1px solid #D49B44', padding: '14px', borderRadius: '12px', marginBottom: '20px' }}>
              <label style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', cursor: 'pointer', fontSize: '0.76rem', color: '#132B20', fontWeight: 700 }}>
                <input type="checkbox" checked={officerConsent} onChange={e => setOfficerConsent(e.target.checked)} style={{ marginTop: '2px' }} />
                <span>I certify as duty officer that the patrol discovery details and seizure memos above are verified accurate under BNSS Sec 105 & Karnataka Police Act.</span>
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button onClick={() => setCurrentStep('step1')} style={btnSecondaryLight}><Edit3 size={15} color="#D49B44" /> Edit Details</button>
              <button onClick={handleSubmitPoliceCase} disabled={isSubmitting} style={{ ...btnPrimaryLight, padding: '12px 24px', fontSize: '0.88rem' }}>
                {isSubmitting ? 'Registering Suo Moto FIR...' : 'Submit & Generate Police Case ID'}
                <CheckCircle2 size={18} color="#D49B44" />
              </button>
            </div>
          </div>
        )}

        {/* CONFIRMATION & UNIQUE POLICE CASE ID GENERATION SCREEN */}
        {currentStep === 'confirmation' && (
          <div style={{ textAlign: 'center', padding: '32px 12px' }}>
            <div style={{
              background: '#132B20',
              border: '2px solid #D49B44',
              color: '#D49B44',
              width: '68px',
              height: '68px',
              borderRadius: '50%',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '18px',
              boxShadow: '0 10px 30px rgba(19, 43, 32, 0.18)'
            }}>
              <CheckCircle2 size={38} color="#D49B44" />
            </div>
            <h3 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#132B20', marginBottom: '6px' }}>
              Police-Initiated Suo Moto FIR Registered!
            </h3>
            <p style={{ fontSize: '0.86rem', color: '#526058', marginBottom: '22px' }}>
              The case record and seizure panchanama have been indexed into the Karnataka State Police Database.
            </p>

            {/* UNIQUE POLICE CASE ID DISPLAY BOX */}
            <div style={{
              background: '#FCFCFA',
              border: '2px dashed #D49B44',
              padding: '22px',
              borderRadius: '20px',
              maxWidth: '480px',
              margin: '0 auto 28px auto',
              boxShadow: '0 6px 20px rgba(19, 43, 32, 0.06)'
            }}>
              <span style={{ fontSize: '0.72rem', color: '#8A5A18', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px' }}>Official Police Case Reference ID</span>
              <div style={{ fontSize: '1.9rem', fontWeight: 900, color: '#132B20', letterSpacing: '1.5px', marginTop: '6px', marginBottom: '6px' }}>
                {refNumber || 'KSP-POL-2026-48912'}
              </div>
              <div style={{ fontSize: '0.76rem', color: '#526058' }}>Reporting Officer: <b style={{ color: '#132B20' }}>{officerName}</b> ({selectedStation})</div>
            </div>

            {/* ACTION BUTTONS */}
            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={downloadPoliceReportPDF}
                style={{
                  background: '#132B20',
                  color: '#D49B44',
                  border: '1px solid #D49B44',
                  padding: '12px 24px',
                  borderRadius: '12px',
                  fontWeight: 800,
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 16px rgba(19, 43, 32, 0.15)'
                }}
              >
                <Download size={18} color="#D49B44" /> Download Official Seizure Report (PDF)
              </button>
              <button
                onClick={handleBack}
                style={{
                  background: '#EFEBE2',
                  color: '#132B20',
                  border: '1.5px solid #D4CEBF',
                  padding: '12px 24px',
                  borderRadius: '12px',
                  fontWeight: 800,
                  fontSize: '0.88rem',
                  cursor: 'pointer'
                }}
              >
                Return to Command Center
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );

  if (isModal) {
    return (
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(19, 43, 32, 0.65)', backdropFilter: 'blur(8px)',
        zIndex: 99999, display: 'flex', justifyContent: 'center', alignItems: 'center',
        padding: '16px'
      }}>
        <div style={{
          width: '100%', maxWidth: '960px', maxHeight: '94vh', borderRadius: '24px',
          boxShadow: '0 25px 60px rgba(19, 43, 32, 0.25)', border: '1px solid #D4CEBF',
          display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative'
        }}>
          {portalContent}
        </div>
      </div>
    );
  }

  return portalContent;
}

const stepCardStyle = {
  background: '#FCFCFA',
  padding: '28px',
  borderRadius: '20px',
  border: '1px solid #D4CEBF',
  boxShadow: '0 8px 24px rgba(19, 43, 32, 0.05)'
};

const stepTitleStyle = {
  fontSize: '1.05rem',
  fontWeight: 900,
  color: '#132B20',
  marginBottom: '18px',
  borderBottom: '2px solid #EAE4D6',
  paddingBottom: '10px',
  display: 'flex',
  alignItems: 'center',
  gap: '8px'
};

const labelStyle = {
  fontSize: '0.76rem',
  fontWeight: 700,
  color: '#132B20',
  display: 'block',
  marginBottom: '4px'
};

const lightInputStyle = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: '10px',
  border: '1px solid #D4CEBF',
  fontSize: '0.82rem',
  marginTop: '2px',
  outline: 'none',
  background: '#FFFFFF',
  color: '#132B20',
  fontWeight: 600,
  boxSizing: 'border-box'
};

const btnPrimaryLight = {
  background: '#132B20',
  color: '#D49B44',
  border: '1px solid #D49B44',
  padding: '10px 20px',
  borderRadius: '10px',
  fontWeight: 800,
  fontSize: '0.84rem',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  boxShadow: '0 4px 14px rgba(19, 43, 32, 0.15)',
  transition: 'all 0.15s ease'
};

const btnSecondaryLight = {
  background: '#EFEBE2',
  color: '#132B20',
  border: '1px solid #D4CEBF',
  padding: '10px 18px',
  borderRadius: '10px',
  fontWeight: 700,
  fontSize: '0.84rem',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  transition: 'all 0.15s ease'
};

export default PoliceInitiatedComplaintPortal;
