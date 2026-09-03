import React, { useMemo } from 'react';

/**
 * ElevenLabsTextStreamer — High-fidelity ElevenLabs-style Word-by-Word Streaming & Karaoke Component
 * (SOLID: SRP — Text tokenization & active word lighting rendering)
 * 
 * - Active/Revealed words: Crisp bold white (#ffffff, font-weight: 800)
 * - Current word: Glowing highlight / active cursor
 * - Upcoming/Unspoken words: Dimmed translucent grey (rgba(255, 255, 255, 0.22))
 */
export default function ElevenLabsTextStreamer({
  text = '',
  currentWordIndex = 9999,
  isStreaming = false,
  isEditing = false,
  editedValue = '',
  onEditedChange,
  placeholder = 'Awaiting speech audio stream...',
  accentColor = '#fbbf24'
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
          background: '#090d16',
          border: '1px solid #475569',
          borderRadius: '12px',
          color: '#f8fafc',
          padding: '14px',
          fontSize: '1.05rem',
          lineHeight: '1.7',
          fontWeight: 600,
          fontFamily: "'Inter', system-ui, sans-serif",
          resize: 'none',
          outline: 'none',
          boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.5)',
          overflowWrap: 'break-word',
          wordBreak: 'break-word'
        }}
      />
    );
  }

  if (words.length === 0) {
    return (
      <div style={{
        color: 'rgba(255, 255, 255, 0.3)',
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
        const isFuture = isStreaming && idx > currentWordIndex;

        return (
          <span
            key={idx}
            className={`elevenlabs-word ${isPast ? 'revealed' : isCurrent ? 'current' : 'upcoming'}`}
            style={{
              display: 'inline',
              color: isCurrent
                ? '#ffffff'
                : isPast
                ? '#f8fafc'
                : 'rgba(255, 255, 255, 0.3)',
              fontWeight: isCurrent ? 800 : isPast ? 600 : 500,
              backgroundColor: isCurrent ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
              borderRadius: isCurrent ? '4px' : '0',
              padding: isCurrent ? '1px 3px' : '0',
              textShadow: isCurrent
                ? '0 0 12px rgba(255, 255, 255, 0.6), 0 0 20px rgba(99, 102, 241, 0.5)'
                : 'none',
              transition: 'color 0.15s ease, background-color 0.15s ease',
              marginRight: '0.32em'
            }}
          >
            {word}
            {isCurrent && (
              <span
                style={{
                  display: 'inline-block',
                  width: '4px',
                  height: '1em',
                  background: '#a855f7',
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
