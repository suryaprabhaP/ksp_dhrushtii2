"""
KSP Sentinel AI — Multimodal Vision & Forensics Blueprint (SOLID: SRP)
======================================================================
Serves REST API routes for:
- POST /api/vision/analyze (Universal Multimodal Endpoint)
- POST /api/vision/ocr_fir (Specialized Bilingual FIR & Document OCR)
- POST /api/vision/cctv_reconstruction (CCTV Scene & Suspect Reconstruction)
"""
import base64
import logging
import time
from typing import List
from flask import Blueprint, jsonify, request

from app.agents.vision_agent import vision_agent

log = logging.getLogger("standalone.blueprint.vision")
vision_bp = Blueprint("vision", __name__)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".jfif"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per image


def _extract_base64_images() -> List[str]:
    """Extracts and normalizes base64 images from either multipart/form-data or JSON payload."""
    images: List[str] = []

    # 1. Check multipart/form-data file uploads
    uploaded_files = request.files.getlist("images") or request.files.getlist("image") or request.files.getlist("file") or request.files.getlist("files")
    for f in uploaded_files:
        if f and f.filename:
            lower = f.filename.lower()
            if any(lower.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
                content = f.read()
                if len(content) <= MAX_IMAGE_SIZE_BYTES:
                    b64_str = base64.b64encode(content).decode("utf-8")
                    images.append(b64_str)
                else:
                    log.warning(f"[VisionBlueprint] File {f.filename} exceeded size limit ({len(content)} bytes)")

    # 2. Check JSON payload
    if not images and request.is_json:
        data = request.get_json(silent=True) or {}
        raw_images = data.get("images") or []
        if isinstance(raw_images, str):
            raw_images = [raw_images]
        for img in raw_images:
            if isinstance(img, str) and img.strip():
                # Strip data URL prefix if present (e.g. data:image/png;base64,...)
                if "base64," in img:
                    img = img.split("base64,")[1]
                images.append(img.strip())

    return images


@vision_bp.route("/api/vision/analyze", methods=["POST"])
def analyze_vision():
    """
    Universal Multimodal Endpoint:
    Accepts 1 to 3 evidence images and an analytical prompt.
    Dispatches to VL-Qwen3.6-35B-A3B through ProviderOrchestrator.
    """
    t0 = time.time()
    images = _extract_base64_images()
    
    # Retrieve query and task parameters
    prompt = request.form.get("prompt") or request.form.get("query") or ""
    task_type = request.form.get("task_type") or "forensics"
    session_id = request.form.get("session_id") or "default_session"

    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = prompt or data.get("prompt") or data.get("query") or ""
        task_type = data.get("task_type") or task_type
        session_id = data.get("session_id") or session_id

    if not images:
        return jsonify({
            "success": False,
            "error": f"No valid images provided. Please upload images in formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        }), 400

    result = vision_agent.analyze_evidence(
        images=images,
        query=prompt,
        task_type=task_type,
        session_id=session_id
    )

    status_code = 200 if result.get("success") else 500
    return jsonify(result), status_code


@vision_bp.route("/api/vision/ocr_fir", methods=["POST"])
def ocr_fir_document():
    """
    Specialized Bilingual FIR & Document OCR Endpoint:
    Extracts structured JSON (FIR number, Sections, Complainant, Accused) from physical documents.
    """
    images = _extract_base64_images()
    prompt = request.form.get("prompt") or (request.get_json(silent=True) or {}).get("prompt") or "Extract all FIR and crime document details into structured JSON."
    session_id = request.form.get("session_id") or (request.get_json(silent=True) or {}).get("session_id") or "default_session"

    if not images:
        return jsonify({
            "success": False,
            "error": "No document images provided for OCR ingestion."
        }), 400

    result = vision_agent.analyze_evidence(
        images=images,
        query=prompt,
        task_type="ocr",
        session_id=session_id
    )

    status_code = 200 if result.get("success") else 500
    return jsonify(result), status_code


@vision_bp.route("/api/vision/cctv_reconstruction", methods=["POST"])
def cctv_reconstruction():
    """
    Specialized CCTV Scene & Suspect Reconstruction Endpoint:
    Analyzes visual crime scene footage, suspects, weapons, and vehicles.
    """
    images = _extract_base64_images()
    prompt = request.form.get("prompt") or (request.get_json(silent=True) or {}).get("prompt") or "Perform forensic CCTV scene reconstruction and identify suspect hallmarks."
    session_id = request.form.get("session_id") or (request.get_json(silent=True) or {}).get("session_id") or "default_session"

    if not images:
        return jsonify({
            "success": False,
            "error": "No CCTV or crime scene images provided for reconstruction."
        }), 400

    result = vision_agent.analyze_evidence(
        images=images,
        query=prompt,
        task_type="cctv",
        session_id=session_id
    )

    status_code = 200 if result.get("success") else 500
    return jsonify(result), status_code
