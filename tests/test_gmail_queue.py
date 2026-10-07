from rescu_growth.gmail_queue import eligible
from rescu_growth.followups import should_follow_up

def test_only_a_tier_review_required():
    assert eligible({"to_email":"a@example.com","tier":"A","status":"REVIEW_REQUIRED"})
    assert not eligible({"to_email":"b@example.com","tier":"B","status":"REVIEW_REQUIRED"})

def test_suppression_blocks():
    assert not eligible({"to_email":"a@example.com","tier":"A","status":"REVIEW_REQUIRED"},{"a@example.com"})

def test_reply_stops_followup():
    assert not should_follow_up("replied",0)
    assert should_follow_up("sent",0)
    assert not should_follow_up("sent",2)
