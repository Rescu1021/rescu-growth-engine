import csv
from pathlib import Path
from .scoring import Lead, score_lead, dedupe
from .export import write_csv

def main():
    rows=[]
    with Path("data/seed_leads.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            campaign=r.pop("campaign")
            rows.append(score_lead(Lead(**r),campaign))
    rows=sorted(dedupe(rows),key=lambda x:x.score,reverse=True)
    out=write_csv(rows,"exports/seed_ranked.csv")
    for x in rows: print(x.tier,x.score,x.name,"->",x.service,"|",x.owner)
    print("Wrote",out)

if __name__=="__main__": main()
