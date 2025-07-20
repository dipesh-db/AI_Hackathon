import json
from pathlib import Path

def load_nursing_license_db():
    """
    Load the nursing license database JSON file from the app folder.
    Returns:
        data (list or dict): Parsed JSON data representing nursing licenses.
    """
    db_path = Path(__file__).parent / "nursing_license_db.json"
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

import re
from datetime import datetime

def normalize_str(val):
    """Lowercase and remove all non-alphanumeric characters."""
    if not val:
        return ""
    return re.sub(r'[^a-z0-9]', '', val.lower())

def normalize_date(date_str):
    """Try to parse date and return ISO format (yyyy-mm-dd). Return empty string if invalid."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except Exception:
            continue
    return ""

def verify_nursing_license(extracted_info, db_data):
    """
    Verify extracted nursing license info against the database.
    Returns detailed mismatches if any field differs.

    Args:
        extracted_info (dict): Extracted fields from the document.
        db_data (list): List of nursing license records.

    Returns:
        bool: True if a matching record is found (all fields match), else False.
        dict: Matched record if found or closest record if mismatches found.
        dict: Mismatches with keys as field names and values as tuple (extracted_value, db_value).
    """

    # Normalize extracted info fields
    extracted_full_name = normalize_str(extracted_info.get("name") or extracted_info.get("full_name"))
    extracted_dob = normalize_date(extracted_info.get("date_of_birth", ""))
    extracted_license_num = normalize_str(extracted_info.get("license_number", ""))
    extracted_gender = normalize_str(extracted_info.get("gender", ""))
    extracted_valid_until = normalize_date(extracted_info.get("valid_until", ""))
    extracted_field_of_practice = normalize_str(extracted_info.get("to_practice_as") or extracted_info.get("field_of_practice"))

    best_match = None
    best_mismatches = None
    fewest_mismatches_count = float('inf')

    for record in db_data:
        record_full_name = normalize_str(record.get("full_name"))
        record_dob = normalize_date(record.get("date_of_birth", ""))
        record_license_num = normalize_str(record.get("license_number", ""))
        record_gender = normalize_str(record.get("gender", ""))
        record_valid_until = normalize_date(record.get("valid_until", ""))
        record_field_of_practice = normalize_str(record.get("field_of_practice"))

        mismatches = {}

        if record_full_name != extracted_full_name:
            mismatches["name"] = (extracted_info.get("name"), record.get("full_name"))
        if record_dob != extracted_dob:
            mismatches["date_of_birth"] = (extracted_info.get("date_of_birth"), record.get("date_of_birth"))
        if record_license_num != extracted_license_num:
            mismatches["license_number"] = (extracted_info.get("license_number"), record.get("license_number"))
        if record_gender != extracted_gender:
            mismatches["gender"] = (extracted_info.get("gender"), record.get("gender"))
        if record_valid_until != extracted_valid_until:
            mismatches["valid_until"] = (extracted_info.get("valid_until"), record.get("valid_until"))
        if record_field_of_practice != extracted_field_of_practice:
            mismatches["field_of_practice"] = (extracted_info.get("field_of_practice"), record.get("field_of_practice"))

        if not mismatches:
            # Perfect match found
            return True, record, {}

        # Track record with fewest mismatches
        if len(mismatches) < fewest_mismatches_count:
            fewest_mismatches_count = len(mismatches)
            best_match = record
            best_mismatches = mismatches

    if best_match:
        return False, best_match, best_mismatches

    # No records found at all (empty db or no similar records)
    return False, None, {"record": ("No record found matching extracted data", None)}
