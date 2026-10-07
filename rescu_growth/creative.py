"""Create deterministic creative briefs from Growth Engine campaign data."""
from .offers import offer_for
from .incentives import incentive_for

BRAND={"plum":"#481B2E","tangerine":"#E7714D","lavender":"#BAA5C0","cerulean":"#DCDFE7","fawn":"#F9E3DB","chalk":"#F7F7F7"}

def brief(campaign, audience, credit_amount="$100"):
    o=offer_for(campaign); inc=incentive_for(campaign,credit_amount)
    return {
      "audience":audience,
      "headline":o["hook"],
      "offer_name":o["name"],
      "offer_stack":o["stack"],
      "primary_cta":o["cta"],
      "secondary_cta":"15-minute Google Meet",
      "incentive":inc["copy"] if inc["eligible"] else "",
      "formats":["1080x1080","1080x1920","1920x1080"],
      "brand":BRAND,
      "visual_rules":["approved Rescu logo only","prefer real Rescu facility/founder imagery","high contrast CTA","mobile-first hierarchy","no medical outcome guarantees"]
    }
