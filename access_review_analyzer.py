#!/usr/bin/env python3
"""
IT Access Governance & Compliance Lab
Educational/simulated access review analyzer.
Uses only Python standard library.
"""

import csv
import json
from collections import Counter
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "access_reviews.csv"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

today = date(2026, 11, 6)

findings = []
summary = Counter()

with INPUT.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        summary["access_items"] += 1
        if row["Review_Decision"] == "Pending":
            summary["pending_reviews"] += 1
        if row["Review_Status"] == "Overdue":
            summary["overdue_reviews"] += 1
        if row["Privileged"] == "Yes":
            summary["privileged_access"] += 1

        issue = None
        rationale = None
        severity = None

        if row["Employment_Status"] == "Terminated":
            issue = "Terminated user retains access"
            rationale = "Employment status is Terminated while an application role remains assigned."
            severity = "High"
        elif row["Privileged"] == "Yes" and int(row["Last_Login_Days"]) >= 60:
            issue = "Stale privileged access"
            rationale = f"Privileged access has not been used for {row['Last_Login_Days']} days."
            severity = "High"
        elif row["Review_Status"] == "Overdue":
            issue = "Access review overdue"
            rationale = "Certification decision was not completed by the review due date."
            severity = "Medium"

        if issue:
            findings.append({
                "Review_ID": row["Review_ID"],
                "User_ID": row["User_ID"],
                "Employee_Name": row["Employee_Name"],
                "Application": row["Application"],
                "Role": row["Role"],
                "Issue": issue,
                "Severity": severity,
                "Rationale": rationale,
                "Recommended_Action": "Validate with manager/application owner, remediate access if required, and retain evidence."
            })
            summary["flagged_items"] += 1
            summary[f"{severity.lower()}_findings"] += 1

out_csv = REPORT_DIR / "access_review_findings.csv"
with out_csv.open("w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "Review_ID","User_ID","Employee_Name","Application","Role",
        "Issue","Severity","Rationale","Recommended_Action"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(findings)

out_json = REPORT_DIR / "access_review_summary.json"
out_json.write_text(json.dumps(dict(summary), indent=2), encoding="utf-8")

print(json.dumps(dict(summary), indent=2))
print(f"\nWrote {out_csv}")
print(f"Wrote {out_json}")
