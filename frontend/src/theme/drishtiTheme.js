/**
 * DRISHTI Tactical Forest Green & Gold Theme Tokens (SOLID Architecture)
 * Strictly adheres to Tactical Forest Green, Amber Gold, Crisp Ivory & Warm Parchment.
 * Zero unstyled / default elements.
 */
export const DRISHTI_THEME = Object.freeze({
  colors: {
    // Primary Foundations
    canvasBg: '#F4F0E8',         // Warm Parchment base canvas (#F4F0E8 / #F7F4EE)
    subHeaderBg: '#FCFCFA',      // Clean Warm Off-White header bar
    cardBg: '#FCFCFA',           // Pure Crisp Ivory for bot cards & bubbles
    inputBg: '#FFFFFF',          // Crisp Ivory White input background
    sidebarDark: '#0D1512',      // Deep Tactical Obsidian/Black
    sidebarSurface: '#18231E',   // Dark charcoal pill (+ New Conversation)
    sidebarBorder: '#1A2B23',    // Subtle dark borders & scrollbar
    sidebarBtnBorder: '#2A3F35', // Subtle button border for charcoal pill
    sidebarActiveNav: '#162820', // Soft glow active navigation item background
    sidebarActiveBorder: '#234E3B', // Active nav item border
    
    // Borders & Dividers
    borderSubtle: '#E5E0D5',     // Subtle Warm Parchment Border
    borderInput: '#DDD7CA',      // Bottom input container rounded border
    borderAccent: '#D49B44',     // Amber Gold Accent Border / Line
    borderGreen: '#132B20',      // Deep Forest Green Border
    borderDropdown: '#D6D1C4',   // Active FIR context subtle border
    borderGlass: 'rgba(212, 155, 68, 0.25)',
    divider: '#1A2B23',
    
    // Forest Green Palette (Primary Brand & Typography)
    forestDark: '#132B20',       // Deep Tactical Forest Green (#132B20)
    forestMid: '#1E4332',        // Hover / Active Forest Green
    forestLight: '#2D5E46',      // Subtle Forest Green
    forestTint: 'rgba(19, 43, 32, 0.08)', // Tint background
    
    // Amber Gold & Tan Palette (Accents, Headers, Badges & Highlights)
    goldAccent: '#D49B44',       // Amber Gold
    goldHover: '#C58B35',        // Darker Amber Gold
    goldLight: '#E8C17C',        // Soft Gold
    goldTan: '#A88B58',          // Muted Gold/Tan nav category header ("COMMAND CENTER", "RECENT SESSIONS")
    goldRead: '#C49746',         // Muted Gold metadata text ("Read")
    goldTint: 'rgba(212, 155, 68, 0.12)', // Gold badge background
    badgePillBg: '#F0EBE1',      // Light sand/parchment sender badge pill
    badgeAccentLine: '#D49B44',  // Vertical Amber Gold left accent line
    
    // Tactical Statuses
    tacticalGreen: '#10B981',    // Emerald Status & Active Icon
    tacticalEmerald: '#34D399',  // Emerald Nav Accent
    tacticalCyan: '#38BDF8',     // Map radar accent
    tacticalPurple: '#A855F7',   // Audio Forensics accent
    tacticalAmber: '#F59E0B',    // Spot FIR accent
    tacticalRed: '#EF4444',      // Urgent alert accent
    
    // Typography Colors
    textPrimary: '#1F2937',      // Primary Prose (Dark Forest Green / Charcoal #1F2937)
    textHeading: '#132B20',      // Deep Tactical Forest Green (#132B20)
    textSecondary: '#4B5563',    // Subtitle Text (Muted Charcoal #4B5563)
    textMuted: '#9CA3AF',        // Placeholder Text (Light gray/sand #9CA3AF)
    textWhite: '#FCFCFA',        // Crisp Off-White for dark backgrounds
    textSidebarNav: '#E5E7EB',   // Off-white nav text (#E5E7EB)
    textSidebarMuted: '#889E90', // Sidebar secondary text
    textNavSlate: '#9CA3AF',     // Soft slate pills text
    
    // Utility & Action Pills
    audioPillBg: '#EAE5DA',      // Muted parchment pill for audio
    audioPillBorder: '#D6D1C4',  // Audio pill border
    actionBtnBg: '#F3EFE6',      // Mic & Plus action buttons background
    actionBtnIcon: '#374151',    // Mic & Plus dark icons (#374151)
    
    // Functional Statuses (Tailored to Tactical Palette)
    success: '#10B981',          // Forest Emerald
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
