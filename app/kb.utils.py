import json
from typing import List, Dict, Optional

# Load KB from JSON file (call once, reuse)
def load_validation_kb(kb_path: str = "app/validation_kb.json") -> List[Dict]:
    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)
    return kb

# Find KB entries matching issue codes
def get_kb_entries_for_issues(kb: List[Dict], issue_codes: List[str]) -> List[Dict]:
    matched_entries = []
    for code in issue_codes:
        for entry in kb:
            if entry.get("issue_code") == code:
                matched_entries.append(entry)
    return matched_entries

# Build prompt string from matched KB entries
def build_prompt_from_kb_entries(kb_entries: List[Dict]) -> str:
    if not kb_entries:
        return "No known issues found for the provided validation failures."

    prompt_parts = ["You are an assistant helping a candidate understand validation issues with their documents. Please provide a clear, empathetic explanation and suggested actions based on the following issues:\n"]

    for entry in kb_entries:
        prompt_parts.append(f"Issue: {entry['title']}\nDescription: {entry['description']}\n")
        prompt_parts.append("Possible causes:\n")
        for cause in entry.get("possible_causes", []):
            prompt_parts.append(f"- {cause}")
        prompt_parts.append("\nRecommended actions:\n")
        for action in entry.get("recommended_actions", []):
            prompt_parts.append(f"- {action}")
        prompt_parts.append("\n")  # spacing between issues

    prompt_parts.append("If any issue is marked critical, please advise the candidate that this will be escalated to HR.\n")
    prompt_parts.append("Answer in a friendly, clear, and helpful tone.")

    return "\n".join(prompt_parts)

