"""Turn scored leads into a small human-review sales queue."""
from dataclasses import dataclass, asdict
from datetime import date

@dataclass
class QueueItem:
    name:str; tier:str; score:int; campaign:str; service:str; owner:str
    city:str=""; phone:str=""; website:str=""; contact_name:str=""
    contact_role:str=""; public_email:str=""; status:str="research"
    next_action:str=""; reason:str=""; last_touch:str=""; outcome:str=""

    def dict(self): return asdict(self)

def readiness(lead):
    points=0
    if getattr(lead,"phone",""): points+=2
    if getattr(lead,"website",""): points+=2
    if getattr(lead,"score",0)>=55: points+=3
    elif getattr(lead,"score",0)>=35: points+=1
    return points

def make_queue(leads,max_per_owner=10):
    out=[]; counts={}
    for x in sorted(leads,key=lambda z:(readiness(z),z.score),reverse=True):
        if x.tier=="C": continue
        if counts.get(x.owner,0)>=max_per_owner: continue
        action="Research decision-maker and personalized partnership angle"
        if x.phone and x.score>=55: action="Human review, then personalized call/intro"
        out.append(QueueItem(x.name,x.tier,x.score,x.campaign,x.service,x.owner,x.city,x.phone,x.website,next_action=action,reason=x.reason))
        counts[x.owner]=counts.get(x.owner,0)+1
    return out
