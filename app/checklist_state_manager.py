# app/checklist_state_manager.py

import json
import os
from app.onboarding_checklist import ONBOARDING_CHECKLIST_TEMPLATE

CHECKLIST_FILE_PATH = "checklist.json"  # You can change this path if needed


def load_checklist():
    """
    Loads the onboarding checklist from a JSON file.
    If the file doesn't exist, returns a fresh copy of the template.
    """
    if os.path.exists(CHECKLIST_FILE_PATH):
        with open(CHECKLIST_FILE_PATH, "r") as f:
            return json.load(f)
    else:
        # Return a deep copy of the template to avoid mutation issues
        import copy
        return copy.deepcopy(ONBOARDING_CHECKLIST_TEMPLATE)


def save_checklist(checklist):
    """
    Saves the current onboarding checklist to disk as JSON.
    """
    with open(CHECKLIST_FILE_PATH, "w") as f:
        json.dump(checklist, f, indent=2)
