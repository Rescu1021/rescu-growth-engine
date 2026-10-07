"""Partner incentive policy. Clinical referrals default to no referral-linked credit."""
CLINICAL_CAMPAIGNS={"ortho_pt","pelvic_floor","ozone_referral","aesthetics"}
NONCLINICAL_CAMPAIGNS={"hbot_sports","fitness","clubs","corporate"}

def incentive_for(campaign, credit_amount=None):
    if campaign in CLINICAL_CAMPAIGNS:
        return {
          "eligible":False,
          "type":"none",
          "copy":"No referral-linked Rescu Credit is offered to clinical referral sources unless specifically cleared under an approved arrangement."
        }
    if campaign in NONCLINICAL_CAMPAIGNS:
        amount = credit_amount if credit_amount is not None else "[APPROVED CREDIT]"
        return {
          "eligible":True,
          "type":"rescu_credit",
          "copy":f"Eligible promotional partners may earn {amount} in Rescu Credit after a qualifying referred client completes the defined paid purchase. Credit is redeemable toward eligible Rescu services, has no cash value, is non-transferable, and is subject to program terms and applicable law."
        }
    return {"eligible":False,"type":"none","copy":""}
