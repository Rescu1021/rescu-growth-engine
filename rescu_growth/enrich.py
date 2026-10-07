"""Conservative enrichment helpers. Public business information only."""
from urllib.parse import urlparse

ROLE_HINTS={
 "hbot_sports":["owner","director","sports performance","physical therapist","coach"],
 "ortho_pt":["owner","clinic director","physical therapist"],
 "pelvic_floor":["owner","clinic director","pelvic health","physical therapist"],
 "fitness":["owner","general manager","fitness director","head coach"],
 "clubs":["general manager","director of racquets","golf professional","athletic director"],
 "aesthetics":["owner","medical director","practice manager"],
 "corporate":["benefits","people operations","human resources","wellness"],
 "ozone_referral":["owner","medical director","physician","practice manager"]
}

def domain(url):
    if not url: return ""
    host=urlparse(url if "://" in url else "https://"+url).netloc.lower()
    return host[4:] if host.startswith("www.") else host

def role_hints(campaign): return ROLE_HINTS.get(campaign,["owner","manager"])
