"""Recycle non-converting leads without spamming them."""
from dataclasses import dataclass, asdict

@dataclass
class RecycleDecision:
    pool:str
    wait_days:int
    owner:str
    reason:str

def recycle(status:str, owner:str, campaign:str, touches:int=0):
    status=(status or "").lower()
    if status in {"opt_out","hard_bounce","bad_contact","not_interested"}:
        return RecycleDecision("SUPPRESSED",0,owner,status)
    if status=="no_reply":
        return RecycleDecision("LONG_NURTURE",30,owner,"No reply after active sequence")
    if status=="meeting_no_book":
        return RecycleDecision("WARM_RECYCLE",14,owner,"Meeting occurred without booking")
    if status=="engaged_no_book":
        return RecycleDecision("WARM_RECYCLE",7,owner,"Engaged but did not book")
    if status=="former_client":
        return RecycleDecision("REACTIVATION",30,owner,"Former-client lifecycle")
    return RecycleDecision("NURTURE",21,owner,"No conversion yet")

def payload(**kwargs): return asdict(recycle(**kwargs))
