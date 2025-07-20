import os
import requests
from dotenv import load_dotenv
from typing import List
import json

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def query_groq_llama(prompt: str, model: str = "llama3-70b-8192") -> str:
    """
    Send a chat completion request to Groq API with the given prompt and model,
    returning the assistant's response text.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful HR assistant helping users with onboarding issues."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"[Error] Groq API call failed: {response.status_code} - {response.text}"

def load_validation_kb(kb_path: str = "app/kb/validation_kb.json") -> List[dict]:
    """
    Load the validation knowledge base (KB) from a JSON file.
    """
    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_kb_entries_for_issues(kb: List[dict], issue_codes: List[str]) -> List[dict]:
    """
    Filter and return KB entries whose 'issue_code' matches any code in issue_codes.
    """
    matched_entries = []
    for code in issue_codes:
        matched_entries.extend([entry for entry in kb if entry.get("issue_code") == code])
    return matched_entries

def build_prompt_from_kb_entries(kb_entries: List[dict]) -> str:
    """
    Construct a detailed prompt string incorporating KB entries to send to Groq LLaMA.
    """
    if not kb_entries:
        return "No known issues found for the provided validation failures."

    prompt_parts = [
        "You are an assistant helping a candidate understand validation issues with their documents. "
        "Please provide a clear, empathetic explanation and suggested actions based on the following issues:\n"
    ]

    for entry in kb_entries:
        prompt_parts.append(f"Issue: {entry['title']}\nDescription: {entry['description']}\n")
        prompt_parts.append("Possible causes:\n")
        for cause in entry.get("possible_causes", []):
            prompt_parts.append(f"- {cause}")
        prompt_parts.append("\nRecommended actions:\n")
        for action in entry.get("recommended_actions", []):
            prompt_parts.append(f"- {action}")
        prompt_parts.append("\n")

    prompt_parts.append(
        "If any issue is marked critical, please advise the candidate that this will be escalated to HR.\n"
        "Answer in a friendly, clear, and helpful tone."
    )

    return "\n".join(prompt_parts)

def generate_human_friendly_message(kb_entries: List[dict]) -> str:
    """
    Generate a static, human-friendly message summarizing validation issues from KB entries.
    Useful for testing or fallback when not calling Groq API.
    """
    if not kb_entries:
        return "Good news! No validation issues were found with your documents."

    message_parts = [
        "I hope you're doing well. I'm reaching out to help you with some minor issues we've encountered during the onboarding process. Don't worry, it's an easy fix!\n",
        "We've noticed a couple of discrepancies with the documents you've submitted, and I'd like to walk you through them.\n"
    ]

    for entry in kb_entries:
        message_parts.append(f"**{entry['title']}**\n")
        message_parts.append(f"{entry['description']}\n")
        message_parts.append("Possible causes:\n")
        for cause in entry.get("possible_causes", []):
            message_parts.append(f"- {cause}\n")
        message_parts.append("Recommended actions:\n")
        for action in entry.get("recommended_actions", []):
            message_parts.append(f"- {action}\n")

        if entry.get("critical", False):
            message_parts.append("\nThis issue is marked as critical and will be escalated to our HR team immediately.\n")

        message_parts.append("\n")  
    message_parts.append(
        "If you have any questions or concerns, please don't hesitate to reach out. We're here to assist you every step of the way.\n\n"
        "Best regards,\nYour HR Assistant"
    )

    return "".join(message_parts)

def get_chatbot_response(issue_codes: List[str], use_template: bool = False) -> str:
    """
    Generate chatbot response for a list of issue codes.

    Parameters:
    - issue_codes: list of validation issue codes detected.
    - use_template: if True, returns static templated message instead of calling Groq API.

    Returns:
    - Response string suitable for displaying to user.
    """
    kb = load_validation_kb()
    entries = get_kb_entries_for_issues(kb, issue_codes)

    if use_template:
        return generate_human_friendly_message(entries)
    else:
        prompt = build_prompt_from_kb_entries(entries)
        return query_groq_llama(prompt)