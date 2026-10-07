"""Seed market map from verified public businesses; bulk collectors can append to this."""
import csv
from pathlib import Path
from .scoring import Lead, score_lead, dedupe
from .queue import make_queue

def load(path="data/market_map.csv"):
    leads=[]
    with Path(path).open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            campaign=r.pop("campaign")
            leads.append(score_lead(Lead(**r),campaign))
    return dedupe(leads)

def main():
    leads=load()
    for q in make_queue(leads,20):
        print(q.owner,q.tier,q.score,q.name,"|",q.next_action)

if __name__=="__main__": main()
