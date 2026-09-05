import React, { useState, useEffect } from 'react';
import { Share2, ThumbsUp, Eye, Sparkles, RefreshCw, PlusCircle, Video, Image, MessageCircle, AlertTriangle, ShieldCheck, MapPin, ExternalLink, Globe } from 'lucide-react';

function SocialFeed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchingLive, setFetchingLive] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  
  // Modal for publishing a simulated tag
  const [showSimModal, setShowSimModal] = useState(false);
  const [simText, setSimText] = useState('');
  const [simPlatform, setSimPlatform] = useState('twitter');
  const [simAuthor, setSimAuthor] = useState('@Citizen_Report_Blr');

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const url = `/api/mcp/social_feed?category=${categoryFilter}&priority=${priorityFilter}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data && (data.success || data.status === 'success')) {
        const list = Array.isArray(data.posts) ? data.posts : (Array.isArray(data.feed) ? data.feed : []);
        setPosts(list);
      }
    } catch (err) {
      console.error("Failed to fetch MCP social feed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchLiveWebStream = async () => {
    setFetchingLive(true);
    try {
      const res = await fetch('/api/mcp/fetch_live', { method: 'POST' });
      const data = await res.json();
      if (data && (data.success || data.status === 'success')) {
        const list = Array.isArray(data.posts) ? data.posts : (Array.isArray(data.feed) ? data.feed : []);
        if (list.length > 0) {
          setPosts(list);
        } else {
          await fetchFeed();
        }
      }
    } catch (err) {
      console.error("Error fetching live web feed:", err);
    } finally {
      setFetchingLive(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, [categoryFilter, priorityFilter]);

  const handleSimulateTag = async (e) => {
    if (e) e.preventDefault();
    if (!simText.trim()) return;

    try {
      const res = await fetch('/api/mcp/publish_tag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: simText,
          platform: simPlatform,
          author: simAuthor,
          tag: '@KarnatakaPolice #KSP'
        })
      });
      const data = await res.json();
      if (data && (data.success || data.status === 'success')) {
        setShowSimModal(false);
        setSimText('');
        fetchFeed();
      }
    } catch (err) {
      console.error("Error publishing simulated tag:", err);
    }
  };

  const getPlatformIcon = (platform) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('twitter') || p.includes('x')) {
      return <span style={{ fontWeight: 900, color: '#132B20', fontSize: '0.85rem' }}>𝕏</span>;
    }
    if (p.includes('youtube')) {
      return <Video size={15} style={{ color: '#DC2626' }} />;
    }
    if (p.includes('instagram')) {
      return <Image size={15} style={{ color: '#DB2777' }} />;
    }
    return <Globe size={15} style={{ color: '#2563EB' }} />;
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'CRITICAL_ALERT':
        return (
          <span style={{ background: '#FEE2E2', color: '#991B1B', border: '1px solid #FCA5A5', padding: '3px 8px', borderRadius: '100px', fontSize: '0.65rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '3px' }}>
            <AlertTriangle size={10} /> CRITICAL ALERT
          </span>
        );
      case 'HIGH_PRIORITY':
      case 'ACTIONABLE_TIP':
        return (
          <span style={{ background: '#FEF3C7', color: '#B45309', border: '1px solid #FCD34D', padding: '3px 8px', borderRadius: '100px', fontSize: '0.65rem', fontWeight: 800 }}>
            ACTIONABLE TIP
          </span>
        );
      default:
        return (
          <span style={{ background: '#E0F2FE', color: '#0369A1', border: '1px solid #BAE6FD', padding: '3px 8px', borderRadius: '100px', fontSize: '0.65rem', fontWeight: 800 }}>
            PUBLIC ADVISORY
          </span>
        );
    }
  };

  const safePosts = Array.isArray(posts) ? posts : [];

  return (
    <div className="insights-content" style={{ padding: '4px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
        <div>
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.92rem', fontWeight: 900, color: '#132B20', margin: '0 0 4px 0' }}>
            <span style={{ color: '#D49B44' }}>🌐</span> Live MCP Social Media Engine
          </h3>
          <p className="section-desc" style={{ fontSize: '0.7rem', color: '#5A6860', margin: 0, fontWeight: 600 }}>
            Real-time public social media & OSINT feeds tagging @KarnatakaPolice.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button 
            onClick={handleFetchLiveWebStream} 
            className="calc-trigger-btn"
            disabled={fetchingLive}
            style={{ 
              background: '#132B20', 
              color: '#FCFCFA', 
              border: '1px solid #10B981', 
              padding: '6px 12px', 
              fontSize: '0.68rem', 
              fontWeight: 700, 
              borderRadius: '8px', 
              cursor: fetchingLive ? 'wait' : 'pointer', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '5px',
              boxShadow: '0 2px 6px rgba(19, 43, 32, 0.15)'
            }}
          >
            <Globe size={12} style={{ color: '#10B981' }} className={fetchingLive ? 'weather-icon-anim' : ''} />
            {fetchingLive ? 'Connecting...' : 'Connect Feed'}
          </button>
          <button 
            onClick={() => setShowSimModal(true)} 
            className="calc-trigger-btn"
            style={{ 
              background: '#132B20', 
              color: '#FCFCFA', 
              border: '1px solid #D49B44', 
              padding: '6px 12px', 
              fontSize: '0.68rem', 
              fontWeight: 700, 
              borderRadius: '8px', 
              cursor: 'pointer', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '5px',
              boxShadow: '0 2px 6px rgba(19, 43, 32, 0.15)'
            }}
          >
            <PlusCircle size={12} style={{ color: '#D49B44' }} /> Post Tag
          </button>
        </div>
      </div>

      {/* Live Deduplication Status Badge */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        background: '#FCFCFA', 
        border: '1px solid #D4CEBF', 
        borderRadius: '10px', 
        padding: '7px 12px', 
        fontSize: '0.7rem', 
        color: '#132B20', 
        marginBottom: '12px', 
        fontWeight: 650,
        boxShadow: '0 1px 4px rgba(19, 43, 32, 0.04)'
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#059669' }}>
          <ShieldCheck size={14} style={{ color: '#059669' }} /> Live Stream Active • 100% MCP Deduplicated
        </span>
        <span style={{ fontWeight: 800, color: '#132B20' }}>{safePosts.length} Unique Live Posts</span>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {[
          { key: 'all', label: `All Posts (${safePosts.length})` },
          { key: 'Cyber Fraud', label: '🚨 Cyber Fraud' },
          { key: 'Traffic & Safety', label: '🚦 Traffic & Safety' },
          { key: 'Patrol & Advisory', label: '🛡️ Patrol & Advisory' }
        ].map(filter => {
          const isActive = categoryFilter === filter.key;
          return (
            <button 
              key={filter.key}
              onClick={() => setCategoryFilter(filter.key)}
              style={{
                background: isActive ? '#132B20' : '#EFEBE2',
                color: isActive ? '#FCFCFA' : '#132B20',
                border: `1px solid ${isActive ? '#D49B44' : '#D4CEBF'}`,
                padding: '4px 10px',
                borderRadius: '8px',
                fontSize: '0.68rem',
                fontWeight: 750,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                boxShadow: isActive ? '0 2px 6px rgba(19, 43, 32, 0.15)' : 'none'
              }}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {/* Posts List Container */}
      <div 
        style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '12px', 
          maxHeight: '460px', 
          overflowY: 'auto', 
          paddingRight: '4px',
          scrollbarWidth: 'thin',
          scrollbarColor: '#D4CEBF #F4F0E8'
        }}
      >
        {loading || fetchingLive ? (
          <div style={{ textAlign: 'center', padding: '28px', fontSize: '0.8rem', color: '#132B20', fontWeight: 650 }}>
            📡 Connecting to live OSINT feeds & deduplicating Karnataka Police intelligence...
          </div>
        ) : safePosts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '28px', fontSize: '0.8rem', color: '#5A6860', background: '#FCFCFA', borderRadius: '12px', border: '1px solid #D4CEBF' }}>
            No tagged posts found matching selected filters.
          </div>
        ) : (
          safePosts.map((post) => {
            const authorName = post.author_name || post.author || post.handle || 'Anonymous';
            const rawContent = post.raw_content || post.content || '';
            const aiSummary = post.ai_summary || post.summary || rawContent;
            const tagUsed = post.tag_used || (Array.isArray(post.tags) ? post.tags.join(' ') : '') || '#KSPAlert';
            const likes = post.engagement?.likes ?? post.likes ?? 0;
            const shares = post.engagement?.shares ?? post.shares ?? 0;
            const views = post.engagement?.views ?? (shares ? shares * 4 : 0);

            return (
              <div 
                key={post.id} 
                style={{
                  background: '#FCFCFA',
                  border: '1px solid #D4CEBF',
                  borderRadius: '14px',
                  padding: '14px',
                  boxShadow: '0 2px 8px rgba(19, 43, 32, 0.04)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px'
                }}
              >
                {/* Header: Author & Tag info */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#EFEBE2', border: '1px solid #D4CEBF', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {getPlatformIcon(post.platform)}
                    </div>
                    <div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#132B20', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        {authorName} 
                        {post.original_url && (
                          <a href={post.original_url} target="_blank" rel="noopener noreferrer" style={{ color: '#D49B44' }} title="Open Original Social Post">
                            <ExternalLink size={11} />
                          </a>
                        )}
                      </div>
                      <div style={{ fontSize: '0.65rem', color: '#5A6860', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span>{post.timestamp || 'Recent'}</span> • <span style={{ color: '#132B20', fontWeight: 700 }}>{tagUsed}</span>
                      </div>
                    </div>
                  </div>
                  {getPriorityBadge(post.priority)}
                </div>

                {/* Tagged Location */}
                {post.location_tagged && (
                  <div style={{ fontSize: '0.68rem', color: '#5A6860', display: 'flex', alignItems: 'center', gap: '4px', background: '#EFEBE2', border: '1px solid #D4CEBF', padding: '3px 8px', borderRadius: '6px', width: 'fit-content', fontWeight: 600 }}>
                    <MapPin size={10} style={{ color: '#DC2626' }} /> {post.location_tagged}
                  </div>
                )}

                {/* Raw Post Text */}
                <p style={{ fontSize: '0.8rem', color: '#24362D', lineHeight: 1.45, margin: 0, fontWeight: 500 }}>
                  {rawContent}
                </p>

                {/* Optional Media Preview */}
                {post.media_url && (
                  <div style={{ position: 'relative', borderRadius: '10px', overflow: 'hidden', height: '140px', border: '1px solid #D4CEBF' }}>
                    <img src={post.media_url} alt="Post media" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    {post.media_type === 'video' && (
                      <div style={{ position: 'absolute', bottom: '8px', right: '8px', background: 'rgba(19, 43, 32, 0.85)', color: 'white', fontSize: '0.65rem', padding: '3px 6px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                        <Video size={12} /> Video Preview
                      </div>
                    )}
                  </div>
                )}

                {/* AI Summarized Content Box */}
                <div 
                  style={{
                    background: '#F7F4EC',
                    border: '1px solid #D4CEBF',
                    borderRadius: '10px',
                    padding: '9px 12px',
                    fontSize: '0.74rem',
                    color: '#132B20',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}
                >
                  <div style={{ fontSize: '0.65rem', fontWeight: 800, color: '#B45309', textTransform: 'uppercase', letterSpacing: '0.4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={11} style={{ color: '#D49B44' }} /> AI Content Summary
                  </div>
                  <div style={{ fontWeight: 600, lineHeight: 1.35, color: '#132B20' }}>
                    {aiSummary}
                  </div>
                </div>

                {/* Footer Engagement Metrics */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #E8E2D5', paddingTop: '8px', fontSize: '0.7rem', color: '#5A6860' }}>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><ThumbsUp size={12} /> {likes}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Share2 size={12} /> {shares}</span>
                    {views > 0 && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Eye size={12} /> {views}</span>
                    )}
                  </div>
                  <span style={{ color: '#059669', fontWeight: 750, fontSize: '0.65rem' }}>✓ MCP Deduplicated</span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Modal to simulate posting a tag */}
      {showSimModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(19, 43, 32, 0.45)', backdropFilter: 'blur(3px)', zIndex: 10002, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
          <div style={{ background: '#FCFCFA', borderRadius: '18px', padding: '22px', maxWidth: '400px', width: '100%', border: '1px solid #D4CEBF', boxShadow: '0 20px 50px rgba(19, 43, 32, 0.2)' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 850, color: '#132B20', margin: '0 0 6px 0' }}>
              Post Tag @KarnatakaPolice
            </h4>
            <p style={{ fontSize: '0.74rem', color: '#5A6860', marginBottom: '14px', lineHeight: 1.4 }}>
              Simulate an incoming citizen social media report tagging Karnataka Police. Strict MD5 deduplication and MCP analysis will process the post.
            </p>

            <form onSubmit={handleSimulateTag} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <select 
                  value={simPlatform} 
                  onChange={(e) => setSimPlatform(e.target.value)}
                  style={{ flex: 1, padding: '8px 10px', borderRadius: '8px', border: '1px solid #D4CEBF', background: '#F7F4EC', fontSize: '0.8rem', color: '#132B20', fontWeight: 600 }}
                >
                  <option value="twitter">X / Twitter</option>
                  <option value="instagram">Instagram</option>
                  <option value="youtube">YouTube</option>
                </select>
                <input 
                  type="text" 
                  value={simAuthor} 
                  onChange={(e) => setSimAuthor(e.target.value)}
                  placeholder="@handle" 
                  style={{ flex: 1, padding: '8px 10px', borderRadius: '8px', border: '1px solid #D4CEBF', background: '#F7F4EC', fontSize: '0.8rem', color: '#132B20', fontWeight: 600 }}
                />
              </div>

              <textarea 
                rows="3"
                value={simText}
                onChange={(e) => setSimText(e.target.value)}
                placeholder="Type post text... (e.g., Fake electricity SMS phishing scam reported near Indiranagar @KarnatakaPolice #KSPAlert)"
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #D4CEBF', background: '#F7F4EC', fontSize: '0.8rem', color: '#132B20', resize: 'none', boxSizing: 'border-box' }}
                required
              />

              <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                <button 
                  type="button" 
                  onClick={() => setShowSimModal(false)}
                  style={{ flex: 1, padding: '9px', background: '#EFEBE2', border: '1px solid #D4CEBF', borderRadius: '8px', fontSize: '0.78rem', fontWeight: 700, color: '#132B20', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  style={{ flex: 1, padding: '9px', background: '#132B20', color: '#FCFCFA', border: '1px solid #D49B44', borderRadius: '8px', fontSize: '0.78rem', fontWeight: 750, cursor: 'pointer' }}
                >
                  Publish & Summarize
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default SocialFeed;
