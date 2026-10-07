"""Prepare Gmail draft payloads. Actual Gmail actions happen in the connected Gmail layer."""
import json
from pathlib import Path

def eligible(row, suppressed=None):
    suppressed={x.lower() for x in (suppressed or set())}
    email=(row.get("to_email") or "").strip().lower()
    return bool(email and row.get("tier")=="A" and email not in suppressed and row.get("status")=="REVIEW_REQUIRED")

def draft_payload(row):
    return {"to":row["to_email"],"subject":row["subject"],"body":row["body"],
            "lead_name":row["name"],"owner":row["owner"],"campaign":row["campaign"]}

def write_payloads(rows,path="exports/gmail_drafts.json",suppressed=None):
    payloads=[draft_payload(r) for r in rows if eligible(r,suppressed)]
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(payloads,indent=2),encoding="utf-8")
    return payloads
