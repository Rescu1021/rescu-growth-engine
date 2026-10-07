"""Build owner-specific work packets from scored leads."""
from .auto_router import route_owner

def build_assignment(lead:dict, copy:dict|None=None):
    routed=route_owner(
        str(lead.get("lead_id","")),
        str(lead.get("campaign","")),
        int(lead.get("score",0)),
        lead.get("tags",[])
    )
    return {
      "lead_id": routed.lead_id,
      "owner": routed.owner,
      "queue": routed.route,
      "priority": "A" if routed.score >= 55 else ("B" if routed.score >= 35 else "C"),
      "reason": routed.reason,
      "outreach": copy or {},
      "send_state": "REVIEW_REQUIRED",
      "next_action": "REVIEW_AND_SEND" if routed.score >= 55 else "REVIEW",
      "stop_conditions":["reply","booking","opt_out","bad_contact","hard_bounce"]
    }
