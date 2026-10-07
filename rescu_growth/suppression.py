"""Permanent outreach suppression registry."""
import csv
from pathlib import Path

def load(path="data/suppression.csv"):
    p=Path(path)
    if not p.exists(): return set()
    with p.open(encoding="utf-8") as f:
        return {(r.get("email") or "").strip().lower() for r in csv.DictReader(f) if r.get("email")}

def add(email,reason,path="data/suppression.csv"):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    exists=p.exists()
    with p.open("a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["email","reason"])
        if not exists: w.writeheader()
        w.writerow({"email":email.strip().lower(),"reason":reason})
