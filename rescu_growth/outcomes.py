"""Simple closed-loop learning from outreach outcomes."""
WEIGHTS={"appointment":20,"partner_meeting":15,"positive_reply":8,"no_reply":-1,"not_interested":-8,"bad_contact":-12}

def outcome_adjustment(outcome):
    return WEIGHTS.get((outcome or "").strip().lower(),0)

def effective_score(base_score,outcome=""):
    return max(0,min(100,int(base_score)+outcome_adjustment(outcome)))
