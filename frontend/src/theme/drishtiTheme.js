/**
 * DRISHTI Tactical Forest Green & Gold Theme Tokens (SOLID Architecture)
 * Strictly adheres to Tactical Forest Green, Amber Gold, Crisp Ivory & Warm Parchment.
 * Zero unstyled / default elements.
 */
export const DRISHTI_THEME = Object.freeze({
  colors: {
    // Primary Foundations
    canvasBg: '#F4F0E8',         // Warm Parchment base canvas
    subHeaderBg: '#FCFCFA',      // Clean Warm Off-White header bar
    cardBg: '#FCFCFA',           // Pure Crisp Ivory for cards & bubbles
    inputBg: '#FCFCFA',          // Crisp Ivory input background
    sidebarDark: '#0A130E',      // Deep Obsidian Forest Green (sidebar)
    sidebarSurface: '#0E1C15',    // Slightly elevated sidebar card/button surface
    sidebarBorder: '#1A3326',    // Dark Green sidebar border
    
    // Borders & Dividers
    borderSubtle: '#D4CEBF',     // Subtle Warm Parchment Border
    borderAccent: '#D49B44',     // Tactical Amber Gold Border
    borderGreen: '#132B20',      // Deep Forest Green Border
    borderGlass: 'rgba(212, 155, 68, 0.25)',
    divider: 'rgba(19, 43, 32, 0.1)',
    
    // Forest Green Palette (Primary Brand & Typography)
    forestDark: '#132B20',       // Deep Tactical Forest Green
    forestMid: '#1E4332',        // Hover / Active Forest Green
    forestLight: '#2D5E46',      // Subtle Forest Green
    forestTint: 'rgba(19, 43, 32, 0.08)', // Tint background
    
    // Amber Gold Palette (Accents, Badges & Highlights)
    goldAccent: '#D49B44',       // Amber Gold
    goldHover: '#C58B35',        // Darker Amber Gold
    goldLight: '#E8C17C',        // Soft Gold
    goldTint: 'rgba(212, 155, 68, 0.12)', // Gold badge background
    goldDark: '#8A5D19',         // Text on gold tint
    goldGlow: 'rgba(212, 155, 68, 0.35)',
    
    // Tactical Statuses
    tacticalGreen: '#10B981',    // Emerald Status
    tacticalCyan: '#38BDF8',     // Map radar accent
    tacticalPurple: '#A855F7',   // Audio Forensics accent
    tacticalAmber: '#F59E0B',    // Spot FIR accent
    tacticalRed: '#EF4444',      // Urgent alert accent
    
    // Typography Colors
    textPrimary: '#132B20',      // Primary Text (Deep Forest Green)
    textSecondary: '#5C584E',    // Secondary Muted Text (Warm Slate)
    textMuted: '#8C877D',        // Light Muted Text
    textWhite: '#FCFCFA',        // Crisp Off-White for dark backgrounds
    textSidebarMuted: '#889E90', // Sidebar secondary text
    
    // Functional Statuses (Tailored to Tactical Palette)
    success: '#1B6A45',          // Forest Emerald
    warning: '#D49B44',          // Amber Gold
    danger: '#B93829',           // Tactical Crimson
    info: '#1E4332',             // Deep Forest Teal
  },
  
  typography: {
    fontHeading: "'Outfit', 'Inter', system-ui, sans-serif",
    fontBody: "'Inter', system-ui, sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sizes: {
      xs: '0.62rem',   // 10px - Badges, sub-labels
      sm: '0.72rem',   // 11.5px - Captions, tags, metadata
      base: '0.82rem', // 13px - Main compact content
      md: '0.9rem',    // 14.5px - Subheaders, button labels
      lg: '1.05rem',   // 17px - Card headers, titles
      xl: '1.25rem'    // 20px - Main screen titles
    },
    lineHeights: {
      tight: 1.2,
      normal: 1.45,
      relaxed: 1.6
    }
  },
  
  shadows: {
    soft: '0 2px 8px rgba(19, 43, 32, 0.05)',
    card: '0 4px 16px rgba(19, 43, 32, 0.08)',
    elevated: '0 8px 24px rgba(19, 43, 32, 0.12)',
    sidebarButton: '0 2px 6px rgba(0, 0, 0, 0.25)',
    userBubble: '0 4px 14px rgba(19, 43, 32, 0.2)',
    goldGlow: '0 0 16px rgba(212, 155, 68, 0.25)',
    greenGlow: '0 0 16px rgba(16, 185, 129, 0.3)',
  },
  
  radii: {
    xs: '4px',
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  }
});
