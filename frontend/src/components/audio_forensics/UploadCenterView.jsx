import React, { useRef } from 'react';
import { Upload, Volume2, Sparkles, FileAudio, AlertTriangle, ShieldCheck, Headphones } from 'lucide-react';
import { FILE_LIMITS } from './constants';

/**
 * UploadCenterView — Centered Drag & Drop Audio Upload Screen in DRISHTI Warm Parchment Theme
 * (SOLID: SRP — Centered Empty/Upload state presentation)
 */
export default function UploadCenterView({
  selectedFile,
  audioUrl,
  isUploading,
  uploadProgress,
  errorMessage,
  onFileSelected,
  onStartTranscribe,
  onLoadSampleAudio
}) {
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelected(file);
  };

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '32px 24px',
      position: 'relative',
      overflowY: 'auto'
    }}>
      {/* Background Decorative Warm Radial Glow */}
      <div style={{
        position: 'absolute',
        width: '500px',
        height: '500px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(212, 155, 68, 0.08) 0%, rgba(19, 43, 32, 0.04) 50%, transparent 70%)',
        pointerEvents: 'none',
        zIndex: 0
      }} />

      {/* Main Crisp Ivory Card Container */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        width: '100%',
        maxWidth: '680px',
        backgroundColor: '#FCFCFA',
        border: '1px solid #D4CEBF',
        borderRadius: '24px',
        padding: '36px',
        boxShadow: '0 15px 35px rgba(19, 43, 32, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center'
      }}>
        {/* Top Header Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: '#EFEBE2',
          border: '1px solid #D4CEBF',
          borderRadius: '20px',
          padding: '6px 14px',
          color: '#132B20',
          fontSize: '0.75rem',
          fontWeight: 800,
          marginBottom: '16px',
          textTransform: 'uppercase',
          letterSpacing: '0.06em'
        }}>
          <ShieldCheck size={14} color="#D49B44" />
          Karnataka State Police • Voice Forensics Lab
        </div>

        <h2 style={{
          fontSize: '1.6rem',
          fontWeight: 800,
          color: '#132B20',
          margin: '0 0 8px 0',
          letterSpacing: '-0.02em'
        }}>
          Upload Voice & Audio Evidence
        </h2>

        <p style={{
          fontSize: '0.86rem',
          color: '#526058',
          margin: '0 0 24px 0',
          maxWidth: '480px',
          lineHeight: '1.5'
        }}>
          Upload witness statements, field recordings, or suspect interrogations. Zoho Zia STT transcribes speech into bilingual Kannada and English evidence narratives with dynamic BNS/IPC legal mapping.
        </p>

        {/* Error Banner if any */}
        {errorMessage && (
          <div style={{
            width: '100%',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '12px',
            padding: '10px 16px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            color: '#DC2626',
            fontSize: '0.8rem',
            fontWeight: 700,
            textAlign: 'left'
          }}>
            <AlertTriangle size={16} flexShrink={0} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Centered Dropzone Area */}
        <div
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{
            width: '100%',
            border: selectedFile ? '2px solid #D49B44' : '1.5px dashed #C2BAAA',
            borderRadius: '18px',
            padding: '32px 20px',
            backgroundColor: selectedFile ? '#EAE4D6' : '#F9F7F2',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
            boxShadow: selectedFile ? '0 0 15px rgba(212, 155, 68, 0.2)' : 'none'
          }}
          onMouseEnter={(e) => {
            if (!selectedFile) e.currentTarget.style.borderColor = '#D49B44';
          }}
          onMouseLeave={(e) => {
            if (!selectedFile) e.currentTarget.style.borderColor = '#C2BAAA';
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={FILE_LIMITS.MIME_ACCEPT}
            style={{ display: 'none' }}
            disabled={isUploading}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) onFileSelected(file);
            }}
          />

          {/* Central Pulsing Icon */}
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: selectedFile ? '#132B20' : '#EAE4D6',
            border: '1px solid #D4CEBF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: selectedFile
              ? '0 4px 14px rgba(19, 43, 32, 0.25)'
              : '0 2px 8px rgba(19, 43, 32, 0.08)'
          }}>
            {selectedFile ? (
              <FileAudio size={28} color="#FCFCFA" />
            ) : (
              <Upload size={28} color="#132B20" />
            )}
          </div>

          {/* Label Text */}
          <div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: '#132B20', marginBottom: '4px' }}>
              {selectedFile ? selectedFile.name : 'Click to Browse or Drag & Drop Recording'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6B7A72' }}>
              {selectedFile ? (
                <span style={{ color: '#0F5132', fontWeight: 800 }}>
                  Ready to Transcribe • {roundSize(selectedFile.size)}
                </span>
              ) : (
                <>Supported formats: <strong style={{ color: '#132B20' }}>.mp3, .wav, .ogg, .m4a, .aac, .flac</strong> (Max {FILE_LIMITS.MAX_SIZE_LABEL})</>
              )}
            </div>
          </div>

          {/* Format Badges */}
          <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
            {FILE_LIMITS.ALLOWED_EXTENSIONS.map((ext) => (
              <span
                key={ext}
                style={{
                  fontSize: '0.65rem',
                  backgroundColor: '#FCFCFA',
                  color: '#132B20',
                  padding: '3px 8px',
                  borderRadius: '6px',
                  border: '1px solid #D4CEBF',
                  fontWeight: 700
                }}
              >
                {ext.toUpperCase()}
              </span>
            ))}
          </div>
        </div>

        {/* Audio Preview Player if Selected */}
        {audioUrl && (
          <div style={{
            width: '100%',
            marginTop: '16px',
            backgroundColor: '#EFEBE2',
            border: '1px solid #D4CEBF',
            borderRadius: '12px',
            padding: '10px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Volume2 size={18} color="#D49B44" />
            <audio
              src={audioUrl}
              controls
              style={{ width: '100%', height: '32px' }}
            />
          </div>
        )}

        {/* Main CTA Button */}
        <button
          disabled={!selectedFile || isUploading}
          onClick={onStartTranscribe}
          style={{
            width: '100%',
            marginTop: '20px',
            padding: '14px',
            backgroundColor: !selectedFile || isUploading ? '#A8A29E' : '#132B20',
            color: '#FCFCFA',
            border: '1px solid #132B20',
            borderRadius: '12px',
            fontSize: '0.92rem',
            fontWeight: 800,
            cursor: !selectedFile || isUploading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            boxShadow: selectedFile && !isUploading ? '0 4px 14px rgba(19, 43, 32, 0.2)' : 'none',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (selectedFile && !isUploading) {
              e.currentTarget.style.backgroundColor = '#0F5132';
              e.currentTarget.style.borderColor = '#D49B44';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedFile && !isUploading) {
              e.currentTarget.style.backgroundColor = '#132B20';
              e.currentTarget.style.borderColor = '#132B20';
            }
          }}
        >
          {isUploading ? (
            <>
              <div className="audio-spinner" /> Transcribing with Zoho Zia STT... ({uploadProgress}%)
            </>
          ) : (
            <>
              <Sparkles size={18} color="#D49B44" /> Run Speech-to-Text Transcription & Legal Mapping
            </>
          )}
        </button>

        {/* Instant Demo Audio Sample Option */}
        <div style={{
          marginTop: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '0.75rem',
          color: '#526058'
        }}>
          <span>Or test instant audio intelligence:</span>
          <button
            type="button"
            disabled={isUploading}
            onClick={onLoadSampleAudio}
            style={{
              backgroundColor: 'rgba(212, 155, 68, 0.08)',
              border: '1px dashed #D49B44',
              color: '#C88A2C',
              borderRadius: '6px',
              padding: '4px 10px',
              fontSize: '0.72rem',
              fontWeight: 800,
              cursor: isUploading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!isUploading) e.currentTarget.style.backgroundColor = 'rgba(212, 155, 68, 0.18)';
            }}
            onMouseLeave={(e) => {
              if (!isUploading) e.currentTarget.style.backgroundColor = 'rgba(212, 155, 68, 0.08)';
            }}
          >
            <Headphones size={13} color="#C88A2C" /> Load Witness Statement Recording
          </button>
        </div>
      </div>
    </div>
  );
}

function roundSize(bytes) {
  if (!bytes) return '0 KB';
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}
