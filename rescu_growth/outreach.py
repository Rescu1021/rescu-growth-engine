"""Build controlled outreach queue. Sending requires explicit downstream action."""
import csv
from pathlib import Path
from .copy import subject,email_body,followup_body
FIELDS=["name","campaign","owner","tier","score","to_email","contact_name","subject","body","status","followup_body"]
def build(items,path="exports/outreach_queue.csv"):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    for x in items:
        email=getattr(x,"public_email","")
        if not email: continue
        rows.append({"name":x.name,"campaign":x.campaign,"owner":x.owner,"tier":x.tier,"score":x.score,"to_email":email,"contact_name":x.contact_name,"subject":subject(x),"body":email_body(x,x.contact_name),"status":"REVIEW_REQUIRED","followup_body":followup_body(x,x.contact_name)})
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    return path
