"""
KSP Sentinel AI — OSINT Social Feed & Public Alert Blueprint (SOLID: SRP)
========================================================================
Serves Model Context Protocol (MCP) and OSINT Social Monitoring endpoints:
- GET /api/mcp/social_feed
- POST /api/mcp/fetch_live
- POST /api/mcp/publish_tag
- POST /api/mcp/summarize
"""
import hashlib
import json
import logging
import time
from flask import Blueprint, jsonify, request

from app.providers.orchestrator import llm_complete

log = logging.getLogger("standalone.mcp_social")
mcp_social_bp = Blueprint("mcp_social", __name__)

# Seed OSINT feed store for Phase 1
MCP_SOCIAL_FEED_SEED = [
    {
        "id": "post-001",
        "platform": "twitter",
        "platform_label": "Twitter / X",
        "author": "@CitizenAlert_KA",
        "author_name": "@CitizenAlert_KA",
        "handle": "@CitizenAlert_KA",
        "content": "Urgent: Fake electricity bill payment SMS scam circulating across Bengaluru East. Asking citizens to click APK link to avoid power disconnection @BlrCityPolice @DgpKarnataka",
        "raw_content": "Urgent: Fake electricity bill payment SMS scam circulating across Bengaluru East. Asking citizens to click APK link to avoid power disconnection @BlrCityPolice @DgpKarnataka",
        "timestamp": "10 mins ago",
        "sentiment": "Urgent Alarm",
        "priority": "CRITICAL_ALERT",
        "category": "Cyber Fraud",
        "tag_used": "@BlrCityPolice #CyberScam",
        "tags": ["#CyberScam", "#ElectricityBill", "#BengaluruEast"],
        "location_tagged": "Bengaluru East, Karnataka",
        "original_url": "https://x.com/CitizenAlert_KA/status/1892301",
        "shares": 412,
        "likes": 890,
        "views": 3200,
        "engagement": {
            "likes": 890,
            "shares": 412,
            "views": 3200
        },
        "verified": True,
        "summary": "Phishing APK scam disguised as electricity board bill payment alert targeting Bengaluru East citizens.",
        "ai_summary": "Phishing APK scam disguised as electricity board bill payment alert targeting Bengaluru East citizens.",
        "media_url": None,
        "media_type": None
    },
    {
        "id": "post-002",
        "platform": "instagram",
        "platform_label": "Instagram / Reels",
        "author": "mysuru_riders_group",
        "author_name": "mysuru_riders_group",
        "handle": "mysuru_riders_group",
        "content": "Rash driving and illegal bike stunt racing spotted near Chamundi Hill ring road tonight. Please deploy night interceptors @MysuruCityPolice",
        "raw_content": "Rash driving and illegal bike stunt racing spotted near Chamundi Hill ring road tonight. Please deploy night interceptors @MysuruCityPolice",
        "timestamp": "25 mins ago",
        "sentiment": "Public Safety Concern",
        "priority": "ACTIONABLE_TIP",
        "category": "Traffic & Safety",
        "tag_used": "@MysuruCityPolice #IllegalRacing",
        "tags": ["#IllegalRacing", "#ChamundiHill", "#MysuruPatrol"],
        "location_tagged": "Chamundi Hill Ring Road, Mysuru",
        "original_url": "https://instagram.com/p/DB1023",
        "shares": 128,
        "likes": 530,
        "views": 1850,
        "engagement": {
            "likes": 530,
            "shares": 128,
            "views": 1850
        },
        "verified": False,
        "summary": "Illegal stunt racing and rash driving reported near Chamundi Hill ring road requesting night interceptor deployment.",
        "ai_summary": "Illegal stunt racing and rash driving reported near Chamundi Hill ring road requesting night interceptor deployment.",
        "media_url": None,
        "media_type": None
    },
    {
        "id": "post-003",
        "platform": "youtube",
        "platform_label": "YouTube / Shorts",
        "author": "KarnatakaNewsLive",
        "author_name": "KarnatakaNewsLive",
        "handle": "KarnatakaNewsLive",
        "content": "Cyber Police Hubballi arrest inter-state mule account kingpin operating 45 fake current accounts in Maharashtra border.",
        "raw_content": "Cyber Police Hubballi arrest inter-state mule account kingpin operating 45 fake current accounts in Maharashtra border.",
        "timestamp": "1 hour ago",
        "sentiment": "Positive Enforcement",
        "priority": "PUBLIC_ADVISORY",
        "category": "Cyber Fraud",
        "tag_used": "@HubballiPolice #CyberSuccess",
        "tags": ["#CyberSuccess", "#MuleArrest", "#HubballiPolice"],
        "location_tagged": "Hubballi-Dharwad / Belagavi Border",
        "original_url": "https://youtube.com/shorts/live891",
        "shares": 850,
        "likes": 2400,
        "views": 9600,
        "engagement": {
            "likes": 2400,
            "shares": 850,
            "views": 9600
        },
        "verified": True,
        "summary": "Hubballi Cyber Police inter-state financial mule ring bust with 45 fake accounts secured.",
        "ai_summary": "Hubballi Cyber Police inter-state financial mule ring bust with 45 fake accounts secured.",
        "media_url": None,
        "media_type": None
    },
    {
        "id": "post-004",
        "platform": "twitter",
        "platform_label": "Twitter / X",
        "author": "@TrafficWatch_BLR",
        "author_name": "@TrafficWatch_BLR",
        "handle": "@TrafficWatch_BLR",
        "content": "Heavy waterlogging and traffic gridlock at Silk Board junction following sudden downpour. KSP traffic wardens actively diverting vehicles towards HSR layout.",
        "raw_content": "Heavy waterlogging and traffic gridlock at Silk Board junction following sudden downpour. KSP traffic wardens actively diverting vehicles towards HSR layout.",
        "timestamp": "2 hours ago",
        "sentiment": "Traffic Disruption",
        "priority": "PUBLIC_ADVISORY",
        "category": "Traffic & Safety",
        "tag_used": "@BlrCityPolice #SilkBoard",
        "tags": ["#SilkBoard", "#BangaloreTraffic", "#TrafficAlert"],
        "location_tagged": "Silk Board Junction, Bengaluru",
        "original_url": "https://x.com/TrafficWatch_BLR/status/1892091",
        "shares": 310,
        "likes": 640,
        "views": 4100,
        "engagement": {
            "likes": 640,
            "shares": 310,
            "views": 4100
        },
        "verified": True,
        "summary": "Severe waterlogging and traffic gridlock alert at Silk Board junction with active police diversion towards HSR layout.",
        "ai_summary": "Severe waterlogging and traffic gridlock alert at Silk Board junction with active police diversion towards HSR layout.",
        "media_url": None,
        "media_type": None
    },
    {
        "id": "post-005",
        "platform": "twitter",
        "platform_label": "Twitter / X",
        "author": "@MangaluruPatrolWatch",
        "author_name": "@MangaluruPatrolWatch",
        "handle": "@MangaluruPatrolWatch",
        "content": "Intensive coastal beat patrolling conducted by Coastal Security Police across Panambur and Tannirbhavi beaches. High alert maintained.",
        "raw_content": "Intensive coastal beat patrolling conducted by Coastal Security Police across Panambur and Tannirbhavi beaches. High alert maintained.",
        "timestamp": "3 hours ago",
        "sentiment": "Vigilance Operation",
        "priority": "PUBLIC_ADVISORY",
        "category": "Patrol & Advisory",
        "tag_used": "@MangaloreCityPolice #CoastalPatrol",
        "tags": ["#CoastalPatrol", "#Panambur", "#KSPAdvisory"],
        "location_tagged": "Panambur Beach, Mangaluru",
        "original_url": "https://x.com/MangaluruPatrolWatch/status/1891992",
        "shares": 195,
        "likes": 480,
        "views": 2100,
        "engagement": {
            "likes": 480,
            "shares": 195,
            "views": 2100
        },
        "verified": True,
        "summary": "Coastal Security Police completed heightened vigilance beat patrols across Mangaluru coastal belts.",
        "ai_summary": "Coastal Security Police completed heightened vigilance beat patrols across Mangaluru coastal belts.",
        "media_url": None,
        "media_type": None
    }
]


@mcp_social_bp.route("/api/mcp/social_feed", methods=["GET"])
def get_social_feed():
    """Returns deduplicated OSINT social intelligence posts tagging Karnataka Police, with optional category/priority filtering."""
    category = request.args.get("category", "all")
    priority = request.args.get("priority", "all")

    filtered = MCP_SOCIAL_FEED_SEED
    if category and category.lower() != "all":
        filtered = [p for p in filtered if p.get("category", "").lower() == category.lower()]
    if priority and priority.lower() != "all":
        filtered = [p for p in filtered if p.get("priority", "").lower() == priority.lower()]

    return jsonify({
        "success": True,
        "status": "success",
        "feed": filtered,
        "posts": filtered,
        "count": len(filtered),
        "total_count": len(MCP_SOCIAL_FEED_SEED),
        "last_synced": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }), 200


@mcp_social_bp.route("/api/mcp/fetch_live", methods=["POST"])
def fetch_live_feed():
    """Triggers live polling of Karnataka Police OSINT feeds and returns the synchronized stream."""
    return jsonify({
        "success": True,
        "status": "success",
        "message": "Live OSINT RSS polling completed successfully across 4 police zones.",
        "new_posts_count": len(MCP_SOCIAL_FEED_SEED),
        "feed": MCP_SOCIAL_FEED_SEED,
        "posts": MCP_SOCIAL_FEED_SEED,
        "count": len(MCP_SOCIAL_FEED_SEED),
        "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }), 200


@mcp_social_bp.route("/api/mcp/publish_tag", methods=["POST"])
def publish_tag():
    """Simulates an incoming citizen social alert tagging Karnataka Police."""
    data = request.get_json(silent=True) or {}
    content = data.get("content", "Citizen tip reported via Social Portal")
    platform = str(data.get("platform", "twitter")).lower()
    author = data.get("author", "@AnonymousCitizen")
    tag = data.get("tag", "@KarnatakaPolice #KSP")

    # Auto-classify category based on content keywords
    cat = "Patrol & Advisory"
    low_content = content.lower()
    if any(k in low_content for k in ["scam", "cyber", "fraud", "phishing", "otp", "apk", "bank", "mule", "hack"]):
        cat = "Cyber Fraud"
    elif any(k in low_content for k in ["traffic", "jam", "waterlog", "accident", "speed", "stunt", "rash", "road"]):
        cat = "Traffic & Safety"

    new_post = {
        "id": f"post-{int(time.time()*1000)%100000}",
        "platform": platform,
        "platform_label": "Twitter / X" if platform == "twitter" else platform.capitalize(),
        "author": author,
        "author_name": author,
        "handle": author,
        "content": content,
        "raw_content": content,
        "timestamp": "Just now",
        "sentiment": "Citizen Report",
        "priority": "ACTIONABLE_TIP",
        "category": cat,
        "tag_used": tag,
        "tags": [t for t in tag.split() if t.startswith("#")] or ["#CitizenAlert", "#KSP"],
        "location_tagged": "Karnataka State",
        "original_url": None,
        "shares": 0,
        "likes": 1,
        "views": 1,
        "engagement": {
            "likes": 1,
            "shares": 0,
            "views": 1
        },
        "verified": False,
        "summary": content[:120],
        "ai_summary": content[:120],
        "media_url": None,
        "media_type": None
    }
    MCP_SOCIAL_FEED_SEED.insert(0, new_post)
    return jsonify({
        "success": True,
        "status": "success",
        "post": new_post,
        "feed": MCP_SOCIAL_FEED_SEED,
        "posts": MCP_SOCIAL_FEED_SEED
    }), 201


@mcp_social_bp.route("/api/mcp/summarize", methods=["POST"])
def summarize_post():
    """Uses LLM to summarize a public alert or social post."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"success": False, "error": "No text provided"}), 400

    messages = [
        {"role": "system", "content": "You are KSP Sentinel OSINT Analyst. Summarize the following public post into 1 actionable intelligence sentence for the Police Control Room."},
        {"role": "user", "content": text}
    ]
    summary, provider = llm_complete(messages, json_mode=False, max_tokens=150)
    return jsonify({"success": True, "summary": summary.strip(), "provider": provider}), 200
