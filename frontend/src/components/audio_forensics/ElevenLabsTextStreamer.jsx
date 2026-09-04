import React, { useMemo } from 'react';

/**
 * ElevenLabsTextStreamer — High-fidelity ElevenLabs-style Word-by-Word Streaming & Karaoke Component
 * (SOLID: SRP — Text tokenization & active word lighting rendering in DRISHTI Light Theme)
 * 
 * - Active/Revealed words: Crisp dark charcoal (#1F2937, font-weight: 600)
 * - Current word: Illuminated Amber Gold badge (#FEF3C7 fill, #D49B44 border, #132B20 bold text)
 * - Upcoming/Unspoken words: Dimmed light grey (#A8A29E)
 */
export default function ElevenLabsTextStreamer({
  text = '',
  currentWordIndex = 9999,
  isStreaming = false,
  isEditing = false,
  editedValue = '',
  onEditedChange,
  placeholder = 'Awaiting speech audio stream...',
  accentColor = '#C88A2C'
}) {
  // Tokenize text into words preserving natural spacing
  const words = useMemo(() => {
    if (!text) return [];
    return text.split(/\s+/).filter(Boolean);
  }, [text]);

  if (isEditing) {
    return (
      <textarea
        value={editedValue}
        onChange={(e) => onEditedChange && onEditedChange(e.target.value)}
        placeholder={placeholder}
        style={{
          flex: 1,
          width: '100%',
          minHeight: '180px',
          backgroundColor: '#FCFCFA',
          border: '1px solid #D4CEBF',
          borderRadius: '12px',
          color: '#132B20',
          padding: '14px',
          fontSize: '1.05rem',
          lineHeight: '1.7',
          fontWeight: 600,
          fontFamily: "'Inter', system-ui, sans-serif",
          resize: 'none',
          outline: 'none',
          boxShadow: 'inset 0 2px 6px rgba(19, 43, 32, 0.05)',
          overflowWrap: 'break-word',
          wordBreak: 'break-word'
        }}
      />
    );
  }

  if (words.length === 0) {
    return (
      <div style={{
        color: '#8A9A90',
        fontSize: '0.95rem',
        fontWeight: 500,
        fontStyle: 'italic',
        marginTop: '16px',
        lineHeight: '1.6'
      }}>
        {placeholder}
      </div>
    );
  }

  return (
    <div
      className="elevenlabs-stream-container"
      style={{
        flex: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        fontSize: '1.05rem',
        lineHeight: '1.75',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        letterSpacing: '-0.01em',
        padding: '6px 2px',
        userSelect: 'text',
        wordBreak: 'break-word',
        overflowWrap: 'break-word',
        whiteSpace: 'normal'
      }}
    >
      {words.map((word, idx) => {
        // If not streaming, all words are fully visible and crisp
        const isPast = !isStreaming || idx < currentWordIndex;
        const isCurrent = isStreaming && idx === currentWordIndex;

        return (
          <span
            key={idx}
            className={`elevenlabs-word ${isPast ? 'revealed' : isCurrent ? 'current' : 'upcoming'}`}
            style={{
              display: 'inline',
              color: isCurrent
                ? '#132B20'
                : isPast
                ? '#1F2937'
                : '#A8A29E',
              fontWeight: isCurrent ? 800 : isPast ? 600 : 500,
              backgroundColor: isCurrent ? '#FEF3C7' : 'transparent',
              border: isCurrent ? '1px solid #D49B44' : 'none',
              borderRadius: isCurrent ? '4px' : '0',
              padding: isCurrent ? '1px 4px' : '0',
              transition: 'color 0.15s ease, background-color 0.15s ease',
              marginRight: '0.32em'
            }}
          >
            {word}
            {isCurrent && (
              <span
                style={{
                  display: 'inline-block',
                  width: '3px',
                  height: '1em',
                  background: '#D49B44',
                  marginLeft: '2px',
                  verticalAlign: '-0.1em',
                  borderRadius: '2px',
                  animation: 'elevenlabs-caret 0.7s infinite'
                }}
              />
            )}
          </span>
        );
      })}
    </div>
  );
}
