"""Automated owner routing for Rescu leads.
Automates assignment/preparation; outbound sending remains approval-gated.
"""
from dataclasses import dataclass, asdict
from typing import Iterable

MYRNA = {"hbot_sports","ortho_pt","fitness","pelvic_floor","corporate","clubs"}
ANA = {"aesthetics"}
CLINICAL = {"ozone_referral"}

@dataclass
class RoutedLead:
    lead_id: str
    campaign: str
    score: int
    owner: str
    route: str
    reason: str
    send_state: str = "REVIEW_REQUIRED"

def route_owner(lead_id:str, campaign:str, score:int, tags:Iterable[str]=()):
    tags={str(x).lower() for x in tags}
    if campaign in ANA or tags & {"trilift","rf microneedling","facial","aesthetics","beauty"}:
        return RoutedLead(lead_id,campaign,score,"Ana","ANA_QUEUE","Aesthetics/service fit")
    if campaign in MYRNA or tags & {"athlete","hbot","gym","club","performance","corporate"}:
        return RoutedLead(lead_id,campaign,score,"Myrna","MYRNA_QUEUE","Performance/partnership fit")
    if campaign in CLINICAL or tags & {"clinical","physician","medical referral"}:
        return RoutedLead(lead_id,campaign,score,"Dr. Taylor","CLINICAL_REVIEW","Clinical/referral relationship")
    return RoutedLead(lead_id,campaign,score,"Review","SHARED_REVIEW","Cross-service or ambiguous fit")

def route_batch(leads):
    return [asdict(route_owner(
        str(x.get("lead_id","")), str(x.get("campaign","")), int(x.get("score",0)), x.get("tags",[])
    )) for x in leads]
