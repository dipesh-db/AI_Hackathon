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
    # Normalize extracted info keys and lower-case strings for insensitive comparison where applicable
    extracted_full_name = (extracted_info.get("name") or extracted_info.get("full_name") or "").strip().lower()
    extracted_dob = extracted_info.get("date_of_birth", "").strip()
    extracted_license_num = extracted_info.get("license_number", "").strip()
    extracted_gender = extracted_info.get("gender", "").strip().lower()
    extracted_valid_until = extracted_info.get("valid_until", "").strip()
    extracted_field_of_practice = (extracted_info.get("to_practice_as") or extracted_info.get("field_of_practice") or "").strip().lower()

    for record in db_data:
        record_full_name = record.get("full_name", "").strip().lower()
        record_dob = record.get("date_of_birth", "").strip()
        record_license_num = record.get("license_number", "").strip()
        record_gender = record.get("gender", "").strip().lower()
        record_valid_until = record.get("valid_until", "").strip()
        record_field_of_practice = record.get("field_of_practice", "").strip().lower()

        mismatches = {}

        if record_full_name != extracted_full_name:
            mismatches["name"] = (extracted_full_name, record_full_name)
        if record_dob != extracted_dob:
            mismatches["date_of_birth"] = (extracted_dob, record_dob)
        if record_license_num != extracted_license_num:
            mismatches["license_number"] = (extracted_license_num, record_license_num)
        if record_gender != extracted_gender:
            mismatches["gender"] = (extracted_gender, record_gender)
        if record_valid_until != extracted_valid_until:
            mismatches["valid_until"] = (extracted_valid_until, record_valid_until)
        if record_field_of_practice != extracted_field_of_practice:
            mismatches["field_of_practice"] = (extracted_field_of_practice, record_field_of_practice)

        if not mismatches:
            # All fields matched perfectly
            return True, record, {}
        else:
            # Return the record with mismatches if found
            return False, record, mismatches

    # No matching record found at all
    return False, None, {"record": "No matching record found"}
