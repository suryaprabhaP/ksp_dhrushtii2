import time
import uuid
import logging
from flask import Blueprint, jsonify, request
from app.services.catalyst_service import catalyst_datastore_service

log = logging.getLogger("standalone.portals")
portals_bp = Blueprint("portals", __name__, url_prefix="/api")

# Resilient in-memory fallback stores
LOCAL_ECOMPLAINTS = []
LOCAL_PASSPORTS = []
LOCAL_POLICE_FIRS = []

# ══════════════════════════════════════════════════════════════════════════════
# E-Complaints Portal Endpoints
# ══════════════════════════════════════════════════════════════════════════════
@portals_bp.route("/complaints", methods=["GET", "POST"])
def manage_complaints():
    if request.method == "POST":
        try:
            data = request.get_json(silent=True) or {}
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            complaint_id = f"KSP-COMP-{int(time.time()*1000)}"
            
            record = {
                "ComplaintId": complaint_id,
                "FirNumber": data.get("fir_number", ""),
                "ComplainantName": data.get("citizen_name", "Anonymous"),
                "Mobile": data.get("phone", "N/A"),
                "Email": data.get("email", ""),
                "IncidentDate": data.get("incident_date", now_str),
                "IncidentLocation": data.get("station", "Unknown"),
                "Division": data.get("division", "Bengaluru"),
                "SubDivision": data.get("sub_division", "Bengaluru"),
                "PoliceStation": data.get("station", "HQ"),
                "CrimeCategory": data.get("category", "General"),
                "ComplaintDescription": data.get("description", ""),
                "SuspectDetails": data.get("suspect_details", ""),
                "EvidenceCount": str(len(data.get("evidence", []))),
                "ComplaintStatus": "PENDING_VERIFICATION",
                "FilingTimestamp": now_str
            }
            
            # 1. Try Cloud insertion
            inserted = catalyst_datastore_service.insert_record("ecomplaints", record)
            
            # 2. Resilient fallback to local storage
            LOCAL_ECOMPLAINTS.insert(0, record)
            
            return jsonify({
                "success": True,
                "acknowledgement_number": complaint_id,
                "status": record["ComplaintStatus"],
                "created_at": now_str,
                "cloud_synced": bool(inserted)
            }), 201
        except Exception as e:
            log.error(f"Complaint registration error: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
            
    else:  # GET
        try:
            records = catalyst_datastore_service.get_records("ecomplaints", limit=200)
            if not records:
                records = list(LOCAL_ECOMPLAINTS)

            station_filter = (request.args.get("station") or request.args.get("police_station") or "").strip().lower()
            division_filter = (request.args.get("division") or request.args.get("district") or "").strip().lower()

            if station_filter:
                records = [
                    r for r in records
                    if station_filter in str(r.get("PoliceStation", "")).lower()
                    or station_filter in str(r.get("IncidentLocation", "")).lower()
                    or station_filter in str(r.get("incident", {}).get("police_station", "")).lower()
                ]

            if division_filter:
                records = [
                    r for r in records
                    if division_filter in str(r.get("Division", "")).lower()
                    or division_filter in str(r.get("SubDivision", "")).lower()
                    or division_filter in str(r.get("district", "")).lower()
                ]

            return jsonify({
                "success": True,
                "count": len(records),
                "complaints": records
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# Passport Verification Endpoints
# ══════════════════════════════════════════════════════════════════════════════
@portals_bp.route("/passports", methods=["GET", "POST"])
def manage_passports():
    if request.method == "POST":
        try:
            data = request.get_json(silent=True) or {}
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            app_id = data.get("application_id", f"PV-2026-{int(time.time()*1000)}")
            
            record = {
                "ApplicationId": app_id,
                "ApplicantName": data.get("applicant_name", "Unknown"),
                "DateOfBirth": data.get("date_of_birth", "1990-01-01"),
                "Gender": data.get("gender", "Unknown"),
                "AadhaarNumber": data.get("aadhaar_number", ""),
                "SubDivision": data.get("sub_division", ""),
                "PoliceStation": data.get("police_station", ""),
                "PassportType": data.get("passport_type", "Fresh"),
                "ApplicationPriority": data.get("priority", "NORMAL"),
                "TravelPurpose": data.get("purpose", ""),
                "TravelCountry": data.get("travel_country", ""),
                "ApplicationStatus": data.get("status", "PENDING"),
                "AssignedConstable": data.get("assigned_constable_name", ""),
                "FieldVisitCompleted": data.get("field_visit_completed", False)
            }
            
            inserted = catalyst_datastore_service.insert_record("passports", record)
            LOCAL_PASSPORTS.insert(0, record)
            return jsonify({"success": True, "record": inserted or record, "cloud_synced": bool(inserted)}), 201
        except Exception as e:
            log.error(f"Passport error: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
            
    else:  # GET
        try:
            records = catalyst_datastore_service.get_records("passports", limit=200)
            if not records:
                records = LOCAL_PASSPORTS
            return jsonify({"success": True, "count": len(records), "records": records}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@portals_bp.route("/passports/<row_id>/status", methods=["PUT"])
def update_passport_status(row_id):
    try:
        data = request.get_json(silent=True) or {}
        update_data = {
            "ApplicationStatus": data.get("status"),
            "FieldVisitCompleted": data.get("field_visit_completed", True)
        }
        success = catalyst_datastore_service.update_record("passports", row_id, update_data)
        
        # Also update local fallback
        for r in LOCAL_PASSPORTS:
            if str(r.get("ROWID")) == str(row_id) or str(r.get("ApplicationId")) == str(row_id):
                r["ApplicationStatus"] = update_data["ApplicationStatus"]
                r["FieldVisitCompleted"] = True
                
        return jsonify({"success": True, "cloud_synced": success}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# Police Initiated Complaints Endpoints
# ══════════════════════════════════════════════════════════════════════════════
@portals_bp.route("/police_firs", methods=["GET", "POST"])
def manage_police_firs():
    if request.method == "POST":
        try:
            data = request.get_json(silent=True) or {}
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            case_id = f"FIR-{int(time.time()*1000)}"
            
            record = {
                "CaseId": case_id,
                "FirNumber": data.get("fir_number", ""),
                "OfficerBadge": data.get("officer_badge", ""),
                "OfficerName": data.get("officer_name", "Unknown"),
                "OfficerRank": data.get("officer_rank", ""),
                "Division": data.get("division", ""),
                "SubDivision": data.get("sub_division", ""),
                "PoliceStation": data.get("police_station", ""),
                "BeatUnit": data.get("beat_unit", ""),
                "CrimeCategory": data.get("crime_category", "General"),
                "IncidentDate": data.get("incident_date", now_str),
                "SpotLocation": data.get("spot_location", ""),
                "SpotNarrative": data.get("spot_narrative", ""),
                "SuspectStatus": data.get("suspect_status", "UNKNOWN"),
                "SuspectName": data.get("suspect_name", ""),
                "SuspectDetails": data.get("suspect_details", ""),
                "SeizedItems": data.get("seized_items", ""),
                "SeizureValue": str(data.get("seizure_value", "0")),
                "PanchaWitness": data.get("pancha_witness", ""),
                "EvidenceCount": str(data.get("evidence_count", "0")),
                "CaseStatus": "FILED",
                "FilingTimestamp": now_str,
                "InvestigationSummary": data.get("investigation_summary", "")
            }
            
            inserted = catalyst_datastore_service.insert_record("police_firs", record)
            LOCAL_POLICE_FIRS.insert(0, record)
            return jsonify({"success": True, "record": inserted or record, "cloud_synced": bool(inserted)}), 201
        except Exception as e:
            log.error(f"FIR error: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
            
    else:  # GET
        try:
            records = catalyst_datastore_service.get_records("police_firs", limit=200)
            if not records:
                records = LOCAL_POLICE_FIRS
            return jsonify({"success": True, "count": len(records), "records": records}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
