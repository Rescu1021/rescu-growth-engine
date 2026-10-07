"""Follow-up state rules: engagement stops automated follow-up."""
STOP={"replied","positive_reply","partner_meeting","appointment","opt_out","not_interested","bad_contact","hard_bounce"}

def should_follow_up(status,followups_sent=0):
    return (status or "").lower() not in STOP and int(followups_sent)<2

def next_state(status,followups_sent=0):
    if not should_follow_up(status,followups_sent): return "STOPPED"
    return "FOLLOWUP_DRAFT_DUE"
