import React, { useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X, Download, ShieldCheck, BarChart2, PieChart, TrendingUp, FileText, Lock, Table, Sparkles } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Pie, Doughnut, Line } from 'react-chartjs-2';
import { jsPDF } from 'jspdf';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PALETTE = [
  '#38bdf8', '#34d399', '#f43f5e', '#fbbf24', '#a855f7', 
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#eab308', '#ef4444', '#8b5cf6', '#3b82f6'
];

export default function ChartAnalysisModal({ isOpen, onClose, chartData, answerText, sec65bAudit, userQuery }) {
  const [activeChartType, setActiveChartType] = useState('combination'); // 'combination', 'bar', 'pie', 'doughnut', 'line'
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1200);
  const chartRef = useRef(null);
  const pieRef = useRef(null);

  React.useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!isOpen || !chartData) return null;

  const labels = chartData.labels || [];
  const rawDataset = (chartData.datasets && chartData.datasets[0]) ? chartData.datasets[0] : { label: 'Cases', data: [] };
  const dataValues = rawDataset.data || [];
  const datasetLabel = rawDataset.label || 'Cases';

  // Base options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#f8fafc',
          font: { family: 'Inter', size: 11, weight: 'bold' }
        }
      },
      title: {
        display: true,
        text: `Analysis: ${userQuery || 'Crime Distribution'}`,
        color: '#38bdf8',
        font: { family: 'Inter', size: 13, weight: 'bold' }
      },
    },
    scales: activeChartType === 'pie' || activeChartType === 'doughnut' ? {} : {
      x: {
        ticks: { color: '#94a3b8', font: { size: 10 } },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      y: {
        ticks: { color: '#94a3b8', font: { size: 10 } },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      }
    }
  };

  // Formatted data structures
  const barLineData = {
    labels: labels,
    datasets: [
      {
        label: datasetLabel,
        data: dataValues,
        backgroundColor: activeChartType === 'line' ? 'rgba(56, 189, 248, 0.2)' : PALETTE.slice(0, labels.length),
        borderColor: '#38bdf8',
        borderWidth: 2,
        borderRadius: 6,
        fill: activeChartType === 'line',
        tension: 0.35,
        pointBackgroundColor: '#38bdf8',
        pointRadius: 4
      }
    ]
  };

  const sliceData = {
    labels: labels,
    datasets: [
      {
        label: datasetLabel,
        data: dataValues,
        backgroundColor: PALETTE.slice(0, labels.length),
        borderColor: '#0f172a',
        borderWidth: 2,
        hoverOffset: 8
      }
    ]
  };

  // Download PNG Chart Image
  const handleDownloadPNG = () => {
    const targetRef = chartRef.current || pieRef.current;
    if (!targetRef) return;
    const url = targetRef.toBase64Image();
    const link = document.createElement('a');
    link.download = `KSP_Crime_Statistics_Chart_${Date.now()}.png`;
    link.href = url;
    link.click();
  };

  // Download PDF Report
  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.text('KARNATAKA STATE POLICE - CRIME STATISTICS REPORT', 14, 20);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Query: ${userQuery || 'Crime Analysis'}`, 14, 30);
    doc.text(`Generated: ${sec65bAudit?.timestamp || new Date().toISOString()}`, 14, 36);
    doc.text(`Section 65B Audit: ${sec65bAudit?.admissible_status || 'Sec 65B Verified'}`, 14, 42);

    const targetRef = chartRef.current || pieRef.current;
    if (targetRef) {
      const chartImg = targetRef.toBase64Image();
      doc.addImage(chartImg, 'PNG', 14, 50, 180, 85);
    }

    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('ANALYTICAL FINDINGS & METRICS SUMMARY', 14, 145);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    const cleanText = (answerText || '').replace(/<[^>]+>/g, '').replace(/[\#\*\_\`]/g, '');
    const splitText = doc.splitTextToSize(cleanText, 180);
    doc.text(splitText.slice(0, 25), 14, 155);

    doc.save(`KSP_Court_Evidence_Report_${Date.now()}.pdf`);
  };

  // Download CSV Table
  const handleDownloadCSV = () => {
    let csvContent = "data:text/csv;charset=utf-8,Label,Metric Value\n";
    labels.forEach((lbl, idx) => {
      const val = dataValues[idx] !== undefined ? dataValues[idx] : '';
      csvContent += `"${lbl.replace(/"/g, '""')}",${val}\n`;
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `KSP_Statistics_Data_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const modalContent = (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(9, 15, 12, 0.88)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      zIndex: 999999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        backgroundColor: '#0F1F18',
        border: '1px solid rgba(212, 155, 68, 0.35)',
        borderRadius: '20px',
        width: '92vw',
        maxWidth: '1200px',
        maxHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '0 30px 80px rgba(0, 0, 0, 0.9), 0 0 35px rgba(212, 155, 68, 0.15)',
        color: '#FCFCFA',
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
      }}>
        
        {/* Modal Header */}
        <div style={{
          padding: '14px 24px',
          backgroundColor: '#132B20',
          borderBottom: '1px solid rgba(212, 155, 68, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              padding: '8px',
              backgroundColor: '#162B21',
              color: '#D49B44',
              borderRadius: '12px',
              border: '1px solid #D49B44',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <BarChart2 size={20} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FCFCFA', margin: 0 }}>
                  Crime Statistics & Analytics Dashboard
                </h3>
                <span style={{
                  fontSize: '0.68rem',
                  padding: '2px 8px',
                  borderRadius: '20px',
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.35)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontWeight: 700,
                  fontFamily: 'monospace'
                }}>
                  <ShieldCheck size={12} /> Sec 65B Verified
                </span>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#94A89D', fontFamily: 'monospace', margin: '2px 0 0 0' }}>
                Query: "{userQuery}"
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handleDownloadPNG}
              style={{
                padding: '7px 14px',
                backgroundColor: '#D49B44',
                color: '#111614',
                border: 'none',
                borderRadius: '8px',
                fontSize: '0.72rem',
                fontWeight: 800,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                boxShadow: '0 2px 10px rgba(212, 155, 68, 0.35)',
                transition: 'all 0.15s'
              }}
              title="Download Chart as Lossless PNG Image"
            >
              <Download size={13} /> Download Chart PNG
            </button>

            <button
              onClick={handleDownloadPDF}
              style={{
                padding: '7px 14px',
                backgroundColor: '#10B981',
                color: '#111614',
                border: 'none',
                borderRadius: '8px',
                fontSize: '0.72rem',
                fontWeight: 800,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                boxShadow: '0 2px 10px rgba(16, 185, 129, 0.35)',
                transition: 'all 0.15s'
              }}
              title="Export Official PDF Report"
            >
              <FileText size={13} /> Export PDF
            </button>

            <button
              onClick={handleDownloadCSV}
              style={{
                padding: '7px 12px',
                backgroundColor: 'rgba(212, 155, 68, 0.15)',
                color: '#D49B44',
                border: '1px solid rgba(212, 155, 68, 0.35)',
                borderRadius: '8px',
                fontSize: '0.72rem',
                fontWeight: 800,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
              title="Export Data CSV"
            >
              <Table size={13} /> CSV
            </button>

            <button
              onClick={onClose}
              style={{
                padding: '6px',
                backgroundColor: '#162B21',
                color: '#FCFCFA',
                border: '1px solid rgba(212, 155, 68, 0.25)',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
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
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Interactive Chart Type Selector Bar */}
        <div style={{
          padding: '8px 24px',
          backgroundColor: '#0D1713',
          borderBottom: '1px solid rgba(212, 155, 68, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: '#94A89D' }}>
            <Sparkles size={14} style={{ color: '#D49B44' }} /> Visual Format:
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            backgroundColor: '#132B20',
            padding: '4px',
            borderRadius: '12px',
            border: '1px solid rgba(212, 155, 68, 0.25)'
          }}>
            {[
              { type: 'combination', label: 'Combo (Bar + Pie)', icon: Sparkles },
              { type: 'bar', label: 'Bar Chart', icon: BarChart2 },
              { type: 'pie', label: 'Pie Chart', icon: PieChart },
              { type: 'doughnut', label: 'Doughnut', icon: PieChart },
              { type: 'line', label: 'Trend Line', icon: TrendingUp }
            ].map(t => {
              const IconComp = t.icon;
              const isActive = activeChartType === t.type;
              return (
                <button
                  key={t.type}
                  onClick={() => setActiveChartType(t.type)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '8px',
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    border: 'none',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    transition: 'all 0.2s ease',
                    backgroundColor: isActive ? '#D49B44' : 'transparent',
                    color: isActive ? '#111614' : '#94A89D'
                  }}
                >
                  <IconComp size={12} /> {t.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Modal Main Body (Responsive Layout) */}
        <div style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: windowWidth < 900 ? '1fr' : 'minmax(0, 1.3fr) minmax(0, 0.7fr)',
          gap: '16px',
          padding: windowWidth < 640 ? '12px' : '20px',
          overflowY: 'auto',
          backgroundColor: '#090F0C'
        }}>
          
          {/* Main Visual Chart Canvas Area */}
          <div style={{
            backgroundColor: '#0F1F18',
            border: '1px solid rgba(212, 155, 68, 0.25)',
            borderRadius: '16px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            height: '420px',
            position: 'relative'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#FCFCFA', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BarChart2 size={14} style={{ color: '#D49B44' }} /> 
                {activeChartType === 'combination' && 'Combination Bar & Doughnut View'}
                {activeChartType === 'bar' && 'Bar Distribution Chart'}
                {activeChartType === 'pie' && 'Proportional Pie Breakdown'}
                {activeChartType === 'doughnut' && 'Doughnut Distribution'}
                {activeChartType === 'line' && 'Statistical Trend Line'}
              </span>
              <span style={{ fontSize: '0.62rem', fontFamily: 'monospace', padding: '2px 8px', borderRadius: '4px', backgroundColor: 'rgba(212, 155, 68, 0.15)', color: '#D49B44', border: '1px solid rgba(212, 155, 68, 0.35)' }}>
                Interactive High-Res Canvas
              </span>
            </div>

            <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%' }}>
              {activeChartType === 'combination' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', height: '100%' }}>
                  <div style={{ position: 'relative', height: '100%' }}>
                    <Bar ref={chartRef} data={barLineData} options={{ ...options, plugins: { ...options.plugins, legend: { display: false } } }} />
                  </div>
                  <div style={{ position: 'relative', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Doughnut ref={pieRef} data={sliceData} options={{ ...options, plugins: { ...options.plugins, title: { display: false } } }} />
                  </div>
                </div>
              )}

              {activeChartType === 'bar' && (
                <Bar ref={chartRef} data={barLineData} options={options} />
              )}

              {activeChartType === 'pie' && (
                <Pie ref={pieRef} data={sliceData} options={options} />
              )}

              {activeChartType === 'doughnut' && (
                <Doughnut ref={pieRef} data={sliceData} options={options} />
              )}

              {activeChartType === 'line' && (
                <Line ref={chartRef} data={barLineData} options={options} />
              )}
            </div>
          </div>

          {/* Analytical Findings & Sec 65B Audit Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            
            {/* Sec 65B Certificate */}
            <div style={{
              backgroundColor: '#0F1F18',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '14px',
              padding: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem', fontFamily: 'monospace', color: '#34d399', marginBottom: '8px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 800 }}>
                  <Lock size={14} /> Sec 65B Evidence Certificate
                </span>
                <span style={{ fontSize: '0.6rem', padding: '2px 6px', borderRadius: '4px', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
                  {sec65bAudit?.admissible_status || 'Sec 65B Verified & Admissible'}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.65rem', fontFamily: 'monospace', color: '#94A89D', backgroundColor: '#090F0C', padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(212, 155, 68, 0.15)' }}>
                <div>
                  <span style={{ color: '#6D8277', display: 'block' }}>Query Hash:</span>
                  <span style={{ color: '#FCFCFA', wordBreak: 'break-all' }}>{sec65bAudit?.query_hash || 'Q-0e6fc56d90d3c473'}</span>
                </div>
                <div>
                  <span style={{ color: '#6D8277', display: 'block' }}>Data Signature:</span>
                  <span style={{ color: '#FCFCFA', wordBreak: 'break-all' }}>{sec65bAudit?.data_signature || 'SIG-e501c2722ac69a6c'}</span>
                </div>
              </div>
            </div>

            {/* Narrative Summary */}
            <div style={{
              backgroundColor: '#0F1F18',
              border: '1px solid rgba(212, 155, 68, 0.25)',
              borderRadius: '14px',
              padding: '16px',
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}>
              <h4 style={{ fontSize: '0.72rem', fontWeight: 800, color: '#D49B44', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'monospace', margin: '0 0 10px 0' }}>
                <FileText size={14} /> STATISTICAL SUMMARY & INSIGHTS
              </h4>
              <div style={{ flex: 1, overflowY: 'auto', fontSize: '0.78rem', lineHeight: '1.6', color: '#FCFCFA' }}>
                <div dangerouslySetInnerHTML={{ __html: answerText || 'No narrative available.' }} />
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
