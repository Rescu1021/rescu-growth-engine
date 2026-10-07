from .offers import offer_for
from .meeting import meeting_cta
from .incentives import incentive_for

def close_block(campaign, bonus_amount=None):
    o=offer_for(campaign)
    inc=incentive_for(campaign,bonus_amount)
    parts=[o["cta"],meeting_cta()]
    if inc["eligible"]: parts.append(inc["copy"])
    return "\n\n".join(x for x in parts if x)
