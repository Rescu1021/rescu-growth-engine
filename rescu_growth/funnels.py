"""Funnel specification generator; produces page content specs, not a SPA."""
from .offers import offer_for
from .incentives import incentive_for

def funnel_spec(campaign,audience,credit_amount="$100"):
    o=offer_for(campaign); inc=incentive_for(campaign,credit_amount)
    sections=[
      {"type":"hero","headline":o["hook"],"cta":o["cta"]},
      {"type":"value_stack","title":o["name"],"items":o["stack"]},
      {"type":"friction","headline":"Start small. Prove the fit. Expand only if it earns its place."},
      {"type":"meeting","headline":"Want to talk it through?","cta":"Choose a 15-minute Google Meet"},
      {"type":"close","headline":"Ready to explore the partnership?","cta":o["cta"]}
    ]
    if inc["eligible"]:
        sections.insert(3,{"type":"partner_credit","headline":"Refer. Reward. Rescu.","body":inc["copy"]})
    return {"campaign":campaign,"audience":audience,"seo_indexable":True,"sections":sections}
