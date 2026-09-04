import React, { useRef, useState } from 'react';
import {
  Globe,
  FileText,
  Edit3,
  RotateCcw,
  Send,
  Trash2,
  Scale,
  MapPin,
  UserCheck,
  Tag,
  Play,
  Pause
} from 'lucide-react';
import ElevenLabsTextStreamer from './ElevenLabsTextStreamer';

/**
 * TranscriptActiveView — ElevenLabs & Spotify Style Bilingual Voice Intelligence Panel in DRISHTI Light Theme
 * (SOLID: SRP — High-fidelity word-by-word streaming & audio sync presentation)
 */
export default function TranscriptActiveView({
  transcriptKn,
  transcriptEn,
  entities,
  activeWordIndexKn = 9999,
  activeWordIndexEn = 9999,
  isStreaming = false,
  isEditing = false,
  editedKn = '',
  editedEn = '',
  processingTimeMs = 0,
  stageId = null,
  audioUrl = null,
  onToggleEdit,
  onReplayStreaming,
  onEditedKnChange,
  onEditedEnChange,
  onDiscard,
  onOpenDisclaimerModal,
  onAudioTimeUpdate
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const current = audioRef.current.currentTime;
    const duration = audioRef.current.duration || 1;
    const progress = Math.min(Math.max(current / duration, 0), 1);
    if (onAudioTimeUpdate) {
      onAudioTimeUpdate(progress);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 24px',
      gap: '14px',
      overflow: 'hidden',
      backgroundColor: '#F4F0E8'
    }}>
      {/* ── TOP BILINGUAL EVIDENCE CARD ── */}
      <div style={{
        flex: 1,
        backgroundColor: '#FCFCFA',
        border: '1px solid #D4CEBF',
        borderRadius: '20px',
        padding: '20px 24px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 15px 35px rgba(19, 43, 32, 0.08)',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* Card Header Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '14px',
          borderBottom: '1px solid #D4CEBF',
          paddingBottom: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#132B20', letterSpacing: '0.04em' }}>
              🎙️ BILINGUAL EVIDENCE TRANSCRIPT
            </span>
            {isStreaming ? (
              <span style={{
                fontSize: '0.7rem',
                backgroundColor: '#EAE4D6',
                color: '#8A5A18',
                border: '1px solid #C4B9A5',
                padding: '2px 10px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: 700
              }}>
                <div className="audio-live-dot" style={{ backgroundColor: '#D49B44' }} /> ElevenLabs Speech-to-Text Streaming...
              </span>
            ) : (
              <span style={{
                fontSize: '0.68rem',
                backgroundColor: '#EAE4D6',
                color: '#0F5132',
                border: '1px solid #C4B9A5',
                padding: '2px 8px',
                borderRadius: '12px',
                fontWeight: 700
              }}>
                ✓ Verified Speech Synthesis
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* Audio Playback Sync Bar */}
            {audioUrl && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#EFEBE2',
                border: '1px solid #D4CEBF',
                borderRadius: '8px',
                padding: '4px 10px'
              }}>
                <audio
                  ref={audioRef}
                  src={audioUrl}
                  onTimeUpdate={handleTimeUpdate}
                  onEnded={handleEnded}
                  style={{ display: 'none' }}
                />
                <button
                  onClick={togglePlay}
                  style={{
                    backgroundColor: '#132B20',
                    color: '#FCFCFA',
                    border: 'none',
                    borderRadius: '50%',
                    width: '24px',
                    height: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}
                  title={isPlaying ? 'Pause Audio' : 'Play Audio & Sync Highlights'}
                >
                  {isPlaying ? <Pause size={12} color="#D49B44" /> : <Play size={12} color="#D49B44" style={{ marginLeft: '1px' }} />}
                </button>
                <span style={{ fontSize: '0.72rem', color: '#132B20', fontWeight: 700 }}>
                  {isPlaying ? 'Playing & Syncing...' : 'Sync Playback'}
                </span>
              </div>
            )}

            <button
              onClick={onToggleEdit}
              style={{
                backgroundColor: isEditing ? '#132B20' : '#EFEBE2',
                color: isEditing ? '#FCFCFA' : '#132B20',
                border: '1px solid #D4CEBF',
                borderRadius: '8px',
                padding: '5px 12px',
                fontSize: '0.74rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s ease'
              }}
            >
              <Edit3 size={13} color={isEditing ? '#D49B44' : '#132B20'} /> {isEditing ? 'Done Editing' : 'Edit Text'}
            </button>

            <button
              disabled={isStreaming}
              onClick={onReplayStreaming}
              style={{
                backgroundColor: '#EFEBE2',
                color: '#526058',
                border: '1px solid #D4CEBF',
                borderRadius: '8px',
                padding: '5px 10px',
                fontSize: '0.74rem',
                cursor: isStreaming ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
              title="Replay ElevenLabs word-by-word streaming animation"
            >
              <RotateCcw size={13} /> Replay
            </button>
          </div>
        </div>

        {/* Dual Column Bilingual Display */}
        <div style={{
          flex: 1,
          minHeight: '260px',
          overflowY: 'auto',
          overflowX: 'hidden',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: '16px',
          padding: '2px'
        }}>
          {/* Column 1: Kannada Original */}
          <div style={{
            minWidth: 0,
            backgroundColor: '#F9F7F2',
            borderRadius: '16px',
            padding: '18px',
            border: '1px solid #D4CEBF',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'inset 0 1px 4px rgba(19, 43, 32, 0.04)',
            overflow: 'hidden'
          }}>
            <div style={{
              fontSize: '0.74rem',
              fontWeight: 800,
              color: '#C88A2C',
              textTransform: 'uppercase',
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              letterSpacing: '0.04em'
            }}>
              <Globe size={14} color="#C88A2C" /> Kannada Spoken Original (ಕನ್ನಡ ಪ್ರತಿಲೇಖನ)
            </div>

            <ElevenLabsTextStreamer
              text={isEditing ? editedKn : transcriptKn}
              currentWordIndex={activeWordIndexKn}
              isStreaming={isStreaming}
              isEditing={isEditing}
              editedValue={editedKn}
              onEditedChange={onEditedKnChange}
              placeholder="Waiting for Kannada speech transcription..."
              accentColor="#C88A2C"
            />
          </div>

          {/* Column 2: English Translation */}
          <div style={{
            minWidth: 0,
            backgroundColor: '#F9F7F2',
            borderRadius: '16px',
            padding: '18px',
            border: '1px solid #D4CEBF',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'inset 0 1px 4px rgba(19, 43, 32, 0.04)',
            overflow: 'hidden'
          }}>
            <div style={{
              fontSize: '0.74rem',
              fontWeight: 800,
              color: '#0F5132',
              textTransform: 'uppercase',
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              letterSpacing: '0.04em'
            }}>
              <FileText size={14} color="#0F5132" /> English Translated Narrative
            </div>

            <ElevenLabsTextStreamer
              text={isEditing ? editedEn : transcriptEn}
              currentWordIndex={activeWordIndexEn}
              isStreaming={isStreaming}
              isEditing={isEditing}
              editedValue={editedEn}
              onEditedChange={onEditedEnChange}
              placeholder="Translated English narrative will stream here..."
              accentColor="#0F5132"
            />
          </div>
        </div>

        {/* Forensic Entity Extraction Strip */}
        {entities && (
          <div style={{
            marginTop: '14px',
            backgroundColor: '#EFEBE2',
            border: '1px solid #D4CEBF',
            borderRadius: '12px',
            padding: '10px 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '10px',
            fontSize: '0.78rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Tag size={13} color="#DC2626" />
                <span style={{ color: '#526058', fontWeight: 600 }}>Category:</span>
                <span style={{ color: '#DC2626', fontWeight: 800 }}>{entities.crime_category || 'General Crime'}</span>
              </div>

              {entities.locations?.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <MapPin size={13} color="#0F5132" />
                  <span style={{ color: '#526058', fontWeight: 600 }}>Locations:</span>
                  {entities.locations.map((loc, i) => (
                    <span key={i} style={{ backgroundColor: '#FCFCFA', color: '#0F5132', padding: '2px 7px', borderRadius: '5px', border: '1px solid #D4CEBF', fontWeight: 700 }}>
                      {loc}
                    </span>
                  ))}
                </div>
              )}

              {entities.suspects?.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <UserCheck size={13} color="#C88A2C" />
                  <span style={{ color: '#526058', fontWeight: 600 }}>Suspects:</span>
                  {entities.suspects.map((susp, i) => (
                    <span key={i} style={{ backgroundColor: '#FCFCFA', color: '#C88A2C', padding: '2px 7px', borderRadius: '5px', border: '1px solid #D4CEBF', fontWeight: 700 }}>
                      {susp}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {entities.bns_sections?.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Scale size={13} color="#132B20" />
                {entities.bns_sections.map((sec, i) => (
                  <span key={i} style={{ backgroundColor: '#EAE4D6', color: '#132B20', border: '1px solid #C4B9A5', padding: '2px 8px', borderRadius: '5px', fontSize: '0.72rem', fontWeight: 700 }} title={sec.title}>
                    {sec.section} ({sec.ipc_equivalent})
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── BOTTOM HUMAN-IN-THE-LOOP ACTION BAR ── */}
      <div style={{
        backgroundColor: '#FCFCFA',
        border: '1px solid #D4CEBF',
        borderRadius: '16px',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
        boxShadow: '0 6px 20px rgba(19, 43, 32, 0.06)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.76rem', color: '#526058' }}>
            Status: <strong style={{ color: '#132B20' }}>{stageId ? 'Staged (Sandboxed in Session)' : 'Idle'}</strong>
          </span>
          {processingTimeMs > 0 && (
            <span style={{ fontSize: '0.72rem', color: '#8A9A90' }}>
              • Zia STT Latency: {processingTimeMs}ms
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={onDiscard}
            style={{
              backgroundColor: '#FEF2F2',
              border: '1px solid #FECACA',
              color: '#DC2626',
              padding: '9px 16px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <Trash2 size={13} /> Discard Evidence
          </button>

          <button
            disabled={!transcriptKn || isStreaming}
            onClick={onOpenDisclaimerModal}
            style={{
              backgroundColor: !transcriptKn || isStreaming
                ? '#A8A29E'
                : '#132B20',
              color: '#FCFCFA',
              border: '1px solid #132B20',
              borderRadius: '10px',
              padding: '10px 22px',
              fontSize: '0.86rem',
              fontWeight: 800,
              cursor: !transcriptKn || isStreaming ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: transcriptKn && !isStreaming ? '0 4px 14px rgba(19, 43, 32, 0.2)' : 'none',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (transcriptKn && !isStreaming) {
                e.currentTarget.style.backgroundColor = '#0F5132';
                e.currentTarget.style.borderColor = '#D49B44';
              }
            }}
            onMouseLeave={(e) => {
              if (transcriptKn && !isStreaming) {
                e.currentTarget.style.backgroundColor = '#132B20';
                e.currentTarget.style.borderColor = '#132B20';
              }
            }}
          >
            <Send size={15} color="#D49B44" /> Send to Investigation Context (RAG) ➔
          </button>
        </div>
      </div>
    </div>
  );
}
