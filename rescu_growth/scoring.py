from dataclasses import dataclass, asdict
from typing import Iterable

CAMPAIGNS = {
    "hbot_sports": {"keywords": ["sports", "athlete", "orthopedic", "physical therapy", "performance", "recovery", "soccer", "basketball", "football", "running", "tennis", "pickleball"], "service": "HBOT / Rescu Performance"},
    "ozone_referral": {"keywords": ["integrative", "functional", "wellness", "longevity", "internal medicine", "primary care"], "service": "Physician-led Ozone Consultation"},
    "ortho_pt": {"keywords": ["orthopedic", "physical therapy", "sports medicine", "rehab", "chiropractic"], "service": "Recovery / Performance"},
    "fitness": {"keywords": ["gym", "fitness", "crossfit", "trainer", "strength", "performance"], "service": "Rescu Performance"},
    "pelvic_floor": {"keywords": ["pelvic", "urogynecology", "urology", "obgyn", "women's health", "physical therapy"], "service": "Emsella / Pelvic Floor"},
    "aesthetics": {"keywords": ["plastic surgery", "dermatology", "med spa", "aesthetic", "facial", "skin"], "service": "TriLift / RF Microneedling / Aesthetics"},
    "corporate": {"keywords": ["corporate", "employer", "executive", "coworking", "business association"], "service": "Corporate Wellness"},
    "clubs": {"keywords": ["golf", "country club", "tennis", "pickleball", "sports club"], "service": "Recovery / Performance Partnership"},
}

@dataclass
class Lead:
    name: str
    category: str = ""
    city: str = ""
    state: str = ""
    website: str = ""
    phone: str = ""
    source: str = ""
    campaign: str = ""
    score: int = 0
    tier: str = "C"
    service: str = ""
    reason: str = ""
    owner: str = ""

    def dict(self):
        return asdict(self)

def score_lead(lead: Lead, campaign: str) -> Lead:
    cfg = CAMPAIGNS[campaign]
    hay = f"{lead.name} {lead.category}".lower()
    score, reasons = 0, []
    hits = [k for k in cfg["keywords"] if k in hay]
    if hits:
        score += min(50, 15 + 8 * len(hits)); reasons.append("campaign fit: " + ", ".join(hits[:4]))
    if lead.phone:
        score += 10; reasons.append("public phone")
    if lead.website:
        score += 8; reasons.append("public website")
    city = lead.city.lower()
    if city == "scarsdale":
        score += 25; reasons.append("Scarsdale priority")
    elif city in {"bronxville","eastchester","new rochelle","harrison","rye","larchmont","pelham","tarrytown","armonk","chappaqua"}:
        score += 18; reasons.append("Westchester priority")
    elif city in {"greenwich","stamford","darien","new canaan"}:
        score += 14; reasons.append("CT expansion corridor")
    if city == "white plains" and campaign in {"ozone_referral","ortho_pt","pelvic_floor","aesthetics"}:
        score -= 12; reasons.append("White Plains clinician deprioritized")
    lead.campaign = campaign
    lead.score = max(0, score)
    lead.tier = "A" if lead.score >= 55 else "B" if lead.score >= 35 else "C"
    lead.service = cfg["service"]
    lead.reason = "; ".join(reasons)
    lead.owner = "Ana" if campaign == "aesthetics" else "Myrna"
    return lead

def dedupe(leads: Iterable[Lead]):
    seen, out = set(), []
    for lead in leads:
        key = (lead.name.strip().lower(), lead.city.strip().lower(), lead.phone.strip())
        if key not in seen:
            seen.add(key); out.append(lead)
    return out
