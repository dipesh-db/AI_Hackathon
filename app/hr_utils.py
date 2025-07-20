import csv
import os
from datetime import datetime

ISSUE_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data_logs", "issue_log.csv")

def save_escalation(employee_name: str, issue_description: str, date: str):
    """
    Append a new HR issue to the issue_log.csv file with timestamp, employee name, issue, and status.
    Creates the file with headers if it doesn't exist.
    """
    print("📥 save_escalation() called with:")
    print(f"👤 Employee Name: {employee_name}")
    print(f"📝 Issue Description: {issue_description}")
    print(f"📅 Date: {date}")

    os.makedirs(os.path.dirname(ISSUE_LOG_PATH), exist_ok=True)

    file_exists = os.path.isfile(ISSUE_LOG_PATH)
    with open(ISSUE_LOG_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "employee_name", "issue_description", "status"])

        if not file_exists:
            print("📄 issue_log.csv does not exist. Creating with headers...")
            writer.writeheader()

        writer.writerow({
            "date": date,
            "employee_name": employee_name,
            "issue_description": issue_description,
            "status": "Open"
        })

    print("✅ Escalation successfully written to issue_log.csv")
