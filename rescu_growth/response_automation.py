"""Response automation policy for Rescu Growth Engine.
Automates routine commercial replies; escalates clinical, sensitive, ambiguous,
negotiated, or high-value conversations to a human owner.
"""
from dataclasses import dataclass, asdict

AUTO_INTENTS={
 "pricing","availability","tell_me_more","booking_request","meeting_request",
 "partnership_interest","common_objection","location_hours","follow_up"
}
ESCALATE_INTENTS={
 "clinical_question","medical_advice","contraindication","adverse_event",
 "complaint","refund","legal","contract_negotiation","custom_pricing",
 "human_requested","unclear"
}

@dataclass
class ResponseDecision:
    action:str
    owner:str
    reason:str
    next_state:str
    max_auto_replies:int=2

def decide(intent:str, owner:str, auto_reply_count:int=0, high_value:bool=False):
    intent=(intent or "unclear").lower()
    if intent in ESCALATE_INTENTS:
        return ResponseDecision("ESCALATE",owner,f"Escalation intent: {intent}","HUMAN_REVIEW")
    if high_value and intent not in {"pricing","availability","location_hours"}:
        return ResponseDecision("ESCALATE",owner,"High-value opportunity","HUMAN_REVIEW")
    if auto_reply_count >= 2:
        return ResponseDecision("ESCALATE",owner,"Automation reply limit reached","HUMAN_REVIEW")
    if intent in AUTO_INTENTS:
        return ResponseDecision("AUTO_REPLY",owner,f"Routine commercial intent: {intent}","AWAITING_REPLY")
    return ResponseDecision("ESCALATE",owner,"Intent uncertain","HUMAN_REVIEW")

def payload(**kwargs): return asdict(decide(**kwargs))
