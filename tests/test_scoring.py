from rescu_growth.scoring import Lead, score_lead

def test_scarsdale_sports_is_high_priority():
    x=score_lead(Lead("Local Sports PT","sports physical therapy","Scarsdale","NY",phone="914"),"hbot_sports")
    assert x.tier == "A"
    assert x.owner == "Myrna"

def test_aesthetics_routes_to_ana():
    x=score_lead(Lead("Skin Center","aesthetic dermatology","Rye","NY",phone="914"),"aesthetics")
    assert x.owner == "Ana"
