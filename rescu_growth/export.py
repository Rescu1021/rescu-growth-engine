import csv
from pathlib import Path

FIELDS=["name","category","city","state","website","phone","source","campaign","score","tier","service","reason","owner"]

def write_csv(leads,path="exports/rescu_leads.csv"):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction="ignore")
        w.writeheader()
        for lead in leads: w.writerow(lead.dict() if hasattr(lead,"dict") else lead)
    return path
