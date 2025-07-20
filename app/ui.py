import streamlit as st
import copy
import os
import requests
from dotenv import load_dotenv
from app.handlers import save_uploaded_files
from app.validator import validate_document_http
from app.onboarding_checklist import ONBOARDING_CHECKLIST_TEMPLATE, update_checklist
from app.db_utils import load_nursing_license_db, verify_nursing_license
from app.chatbot import get_chatbot_response
import re
import json
from datetime import datetime
from .hr_utils import save_escalation

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
            all_failed_issues_with_notes = {}  # dictionary to accumulate failed issues with detailed notes

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

                # Collect failed issues with their notes for chatbot context
                for key, result in validation_results.items():
                    if result.get("status") != "PASS" and (allowed_fields is None or key in allowed_fields):
                        all_failed_issues_with_notes[key] = result.get("notes", "No details provided.")

                # Instead of rendering full report here, just show a brief status
                if all(result.get("status") == "PASS" for result in validation_results.values()):
                    st.success(f"✅ `{doc_type}` validated successfully.")
                else:
                    st.warning(f"⚠️ `{doc_type}` has validation issues. Please ask the chatbot for details.")

                if doc_type in checklist:
                    checklist = update_checklist(checklist, doc_type, validation_results, notes=report.get("notes", ""))

            # Save failed issues with notes in session state for chatbot to access
            st.session_state.pending_validation_issues = all_failed_issues_with_notes

            # Show overall onboarding progress after validation
            progress = calculate_onboarding_progress(checklist)
            st.subheader("📊 Onboarding Progress")
            st.progress(progress / 100)
            st.write(f"Overall Completion: {progress}%")

    else:
        st.info("Please upload one or more documents to begin validation.")


def chatbot_panel():
    st.header("🧠 Chat with Onboarding Copilot")

    # Friendly descriptions for common validation issues
    ISSUE_DESCRIPTIONS = {
        "name_mismatch": "The extracted name does not match the expected name on file.",
        "dob_mismatch": "The date of birth did not match the expected record.",
        "license_number_mismatch": "The license number provided does not match our records.",
        "validity_date_mismatch": "The license expiry date appears to be invalid or expired.",
        "field_missing": "One or more required fields are missing in the document.",
        "database_check": "Verification against the official nursing license database failed."
    }

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_validation_issues" not in st.session_state:
        st.session_state.pending_validation_issues = {}

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input prompt
    user_input = st.chat_input("Ask a question like 'what was wrong with my document?'", key="chatbot_input_unique")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build detailed context notes from validation issues
        issues = st.session_state.pending_validation_issues
        if issues:
            context_lines = []
            for key, note in issues.items():
                friendly_desc = ISSUE_DESCRIPTIONS.get(key, key.replace("_", " ").capitalize())
                context_lines.append(f"- {friendly_desc}: {note}")
            context_notes = "\n".join(context_lines)
        else:
            context_notes = "There are no known validation issues right now."

        # System prompt with escalation instructions
        system_prompt = (
            "You are a helpful and friendly onboarding assistant chatbot. "
            "Your job is to help users understand issues found in their uploaded documents, "
            "explain HR and compliance policies clearly, and provide step-by-step guidance on how to fix errors. "
            "Use the following list of validation issues as context to your answers:\n"
            + context_notes + "\n"
            "If the user asks about an issue not listed here, respond politely that you don't have that information.\n"
            "If the user seems frustrated, apologize for the inconvenience and ask if they would like to escalate the issue to HR.\n"
            "If the user wants to escalate, ask for their full name and a brief description of the issue in a natural conversational way.\n"
            "Once you have collected the name and issue, respond with a confirmation message and include a JSON object enclosed in triple backticks "
            "at the end of your message containing the escalation details in the following format STRICTLY:\n"
            "```json\n"
            "{\n"
            "  \"escalation\": {\n"
            "    \"name\": \"<user full name>\",\n"
            "    \"issue\": \"<issue description>\",\n"
            "  }\n"
            "}\n"
            "```\n"
            "display the JSON object to the user in the chat UI; it is also for backend processing"
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ] + st.session_state.chat_history[-6:]

        # Call Groq API and process response
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            full_response = res.json()["choices"][0]["message"]["content"]

            # Extract JSON escalation block
            json_match = re.search(r"```json(.*?)```", full_response, re.DOTALL)
            escalation_data = None
            if json_match:
                json_text = json_match.group(1).strip()
                try:
                    escalation_json = json.loads(json_text)
                    escalation_data = escalation_json.get("escalation")
                except json.JSONDecodeError:
                    escalation_data = None
                
                user_friendly_response = re.sub(r"```json.*?```", "", full_response, flags=re.DOTALL).strip()
            else:
                user_friendly_response = full_response
             
            # Save escalation if present
            if escalation_data:
                print("Escalation data found:", escalation_data)
                if "date" not in escalation_data or not escalation_data["date"]:
                    escalation_data["date"] = datetime.now().strftime("%Y-%m-%d")
                print("📤 About to call save_escalation with:", escalation_data)    
                save_escalation(
                    employee_name=escalation_data.get("name", "Unknown"),
                    issue_description=escalation_data.get("issue", "No description provided."),
                    date=escalation_data.get("date")
                )

        except Exception as e:
            user_friendly_response = (
                f"⚠️ Sorry, something went wrong when contacting the assistant API.\n\n"
                f"Error details: `{e}`"
            )

        with st.chat_message("assistant"):
            st.markdown(user_friendly_response)
        st.session_state.chat_history.append({"role": "assistant", "content": user_friendly_response})

chatbot_panel()