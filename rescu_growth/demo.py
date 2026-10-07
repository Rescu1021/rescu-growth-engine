import csv
from pathlib import Path
from .scoring import Lead, score_lead, dedupe

SAMPLE = [
    Lead("Scarsdale Sports Performance", "sports performance physical therapy", "Scarsdale", "NY", "https://example.com", "914-555-0101", "demo"),
    Lead("Greenwich Integrative Wellness", "integrative functional wellness", "Greenwich", "CT", "https://example.org", "203-555-0102", "demo"),
    Lead("Westchester Pickleball Club", "pickleball sports club", "Rye", "NY", "", "914-555-0103", "demo"),
]

def main():
    rows=[]
    for lead,campaign in zip(SAMPLE,["hbot_sports","ozone_referral","clubs"]):
        rows.append(score_lead(lead,campaign))
    rows=dedupe(rows)
    out=Path("rescu_growth_demo.csv")
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].dict()))
        w.writeheader(); w.writerows([r.dict() for r in rows])
    for r in rows:
        print(r.tier, r.score, r.name, "->", r.service, "| owner:", r.owner)
    print("Wrote", out)

if __name__ == "__main__": main()
