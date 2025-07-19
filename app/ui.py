import streamlit as st
import copy
from app.handlers import save_uploaded_files
from app.validator import validate_document_http
from app.onboarding_checklist import ONBOARDING_CHECKLIST_TEMPLATE, update_checklist
from app.db_utils import load_nursing_license_db, verify_nursing_license

# Load nursing license DB once on app start
nursing_license_db = load_nursing_license_db()

def calculate_onboarding_progress(checklist):
    """
    Calculate onboarding progress as % of documents fully validated.
    Only count fields if the entire document is validated (all fields PASS).
    """
    total_fields = 0
    passed_fields = 0

    for doc_data in checklist.values():
        fields = doc_data.get("required_fields", {})
        total_fields += len(fields)
        # Check if all fields passed
        all_passed = all(status == "PASS" for status in fields.values())
        if all_passed:
            # Count all fields as passed only if all passed
            passed_fields += len(fields)
        # else do not count any fields from this document

    if total_fields == 0:
        return 0
    return round((passed_fields / total_fields) * 100, 2)


def upload_section():
    st.header("Upload Onboarding Documents")

    uploaded_files = st.file_uploader(
        "Choose files (PDF, images, or scans)",
        accept_multiple_files=True,
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_files:
        saved_paths = save_uploaded_files(uploaded_files)
        st.success(f"{len(saved_paths)} file(s) saved to disk.")

        checklist = copy.deepcopy(ONBOARDING_CHECKLIST_TEMPLATE)

        if st.button("Validate Documents"):
            for path in saved_paths:
                st.write(f"📁 Validating `{path}`...")
                report = validate_document_http(path)

                doc_type = report.get("document_type", None)
                allowed_fields = []

                # Add database_check field if Nursing License
                if doc_type in ONBOARDING_CHECKLIST_TEMPLATE:
                    allowed_fields = list(ONBOARDING_CHECKLIST_TEMPLATE[doc_type]["required_fields"].keys())
                    if doc_type == "Nursing License":
                        allowed_fields.append("database_check")  # To display DB verification

                validation_results = report.get("validation", {})
                extracted_info = report.get("extracted_info", {})

                # Verify nursing license data against DB and update validation results
                if doc_type == "Nursing License":
                    is_valid, matched_record, mismatches = verify_nursing_license(extracted_info, nursing_license_db)
                    if is_valid:
                        validation_results["database_check"] = {
                            "status": "PASS",
                            "notes": "Nursing license data verified successfully against database."
                        }
                    else:
                        notes = "Nursing license data does not match database records."
                        if mismatches:
                            notes += "\nMismatched fields:\n"
                            for field, (extracted_val, db_val) in mismatches.items():
                                notes += f"- {field}: extracted='{extracted_val}', db='{db_val}'\n"
                        validation_results["database_check"] = {
                            "status": "FAIL",
                            "notes": notes
                        }
                    # Update report validation so UI shows DB check status
                    report["validation"] = validation_results

                render_validation_report(report, allowed_fields)

                if doc_type in checklist:
                    checklist = update_checklist(checklist, doc_type, validation_results, notes=report.get("notes", ""))

            # Show overall onboarding progress after validation
            progress = calculate_onboarding_progress(checklist)
            st.subheader("📊 Onboarding Progress")
            st.progress(progress / 100)
            st.write(f"Overall Completion: {progress}%")

    else:
        st.info("Please upload one or more documents to begin validation.")

def render_validation_report(report: dict, allowed_fields=None):
    if "error" in report:
        st.error(report["error"])
        if "details" in report:
            st.text(report["details"])
        if "raw_response" in report:
            st.text(report["raw_response"])
        return

    doc_type = report.get("document_type", "Unknown")
    st.subheader(f"Document Type: {doc_type}")

    validation = report.get("validation", {})

    # Check if all fields passed
    all_passed = all(
        (result.get("status") == "PASS" for key, result in validation.items() if allowed_fields is None or key in allowed_fields)
    )

    if all_passed:
        st.success("✅ All fields validated successfully!")
        return  # No need to show details if all passed

    # If not all passed, show failed fields with reasons
    st.error("⚠️ Validation Issues Found:")
    for key, result in validation.items():
        if allowed_fields and key not in allowed_fields:
            continue

        status = result.get("status", "UNKNOWN")
        notes = result.get("notes", "")

        if status != "PASS":
            field_name = key.replace("_", " ").capitalize()
            st.markdown(f"**{field_name}:** ❌ {notes}")

    # Optionally: offer a collapsible debug section to show extracted info only if needed
    with st.expander("Show extracted information (for debugging)"):
        extracted = report.get("extracted_info", {})
        for key, value in extracted.items():
            label = key.replace("_", " ").capitalize()
            st.write(f"**{label}:** {value}")
