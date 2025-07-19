# onboarding_checklist.py

# Mapping of required fields for each document type
DOCUMENT_FIELD_MAPPING = {
    "Employment Contract": [
        "employee_name", "start_date", "position", "signature"
    ],
    "Nursing License": [
        "name",
        "date_of_birth",
        "license_number",
        "gender",
        "to_practice_as",
        "valid_until",
        "database_check"  # Added to include DB verification as required field
    ],
}

# Template structure for onboarding checklist,
# initializes required fields with status "Pending"
ONBOARDING_CHECKLIST_TEMPLATE = {
    doc_type: {
        "status": "Pending",
        "notes": "",
        "required_fields": {field: "Pending" for field in fields}
    }
    for doc_type, fields in DOCUMENT_FIELD_MAPPING.items()
}

def update_checklist(checklist, document_type, validation_results, notes=None):
    """
    Update the onboarding checklist for the given document type using validation results.

    Args:
        checklist (dict): Current checklist state.
        document_type (str): Type of document being updated.
        validation_results (dict): Validation results keyed by field name,
                                   each with 'status' and 'notes'.
        notes (str, optional): Additional notes to append to checklist.

    Returns:
        dict: Updated checklist.
    """
    # Add generic entry if document type is unknown
    if document_type not in checklist:
        checklist[document_type] = {
            "status": "Unknown Document",
            "notes": "Document type not recognized in onboarding checklist.",
            "required_fields": {}
        }
        return checklist

    # Ensure 'notes' key exists and is string
    checklist[document_type]["notes"] = checklist[document_type].get("notes") or ""

    fields = checklist[document_type]["required_fields"]

    all_passed = True  # Track if all required fields passed validation

    for field in fields:
        if field in validation_results:
            status = validation_results[field].get("status", "FAIL")
            field_notes = validation_results[field].get("notes", "")
            fields[field] = status
            if status != "PASS":
                all_passed = False
                checklist[document_type]["notes"] += f"{field}: {field_notes}\n"
        else:
            # Field missing in validation results => mark as FAIL
            fields[field] = "FAIL"
            all_passed = False
            checklist[document_type]["notes"] += f"{field}: Missing in validation results.\n"

    # Update overall status based on fields
    checklist[document_type]["status"] = "Completed" if all_passed else "Incomplete"

    # Append any additional notes passed to function
    if notes:
        checklist[document_type]["notes"] += notes

    return checklist
