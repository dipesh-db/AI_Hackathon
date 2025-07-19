import os
import base64
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def validate_document_http(file_path: str) -> dict:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_API_BASE")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not all([api_key, endpoint, deployment_name, api_version]):
        return {"error": "Missing one or more environment variables."}

    url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

    file_path = Path(file_path)
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    with open(file_path, "rb") as f:
        image_bytes = f.read()

    base64_image = base64.b64encode(image_bytes).decode()

    prompt = (
    """You are an assistant that analyzes scanned onboarding documents.

Step 1: Identify the type of document. Examples include: Employment Contract, Nursing License, etc.

Step 2: Based on the identified document type, check if all required fields are present and clear. For example:

- Employment Contract: employee_name, start_date, position, signature
- Nursing License: name, date_of_birth, license_number, gender, to_practice_as, valid_until

Step 3: Extract all required information fields.

Step 4: For each required field, indicate if it is present and clear ("PASS") or missing/unclear ("FAIL") with notes.

Step 5: If the document type does not match the expected onboarding document types, respond accordingly.

Please respond in the following JSON format:

{
  "document_type": "Detected Document Type",
  "validation": {
    "field_name": {"status": "PASS/FAIL", "notes": "..."},
    ...
  },
  "extracted_info": {
    "field_name": "extracted value",
    ...
  },
  "notes": "Any additional observations"
}"""


)

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    json_data = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a helpful assistant that validates scanned onboarding documents."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(url, headers=headers, json=json_data)

    if response.status_code == 200:
        try:
            content = response.json()["choices"][0]["message"]["content"]

            # Strip markdown code fences if present
            if content.startswith("```json"):
                content = content[len("```json"):]

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from AI response.", "raw_response": content}
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}
