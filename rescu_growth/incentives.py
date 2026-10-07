"""Partner incentive policy. Clinical referrals default to no per-patient compensation."""
CLINICAL_CAMPAIGNS={"ortho_pt","pelvic_floor","ozone_referral","aesthetics"}
NONCLINICAL_CAMPAIGNS={"hbot_sports","fitness","clubs","corporate"}

def incentive_for(campaign, bonus_amount=None):
    if campaign in CLINICAL_CAMPAIGNS:
        return {
          "eligible":False,
          "type":"none",
          "copy":"No per-patient referral compensation is offered to clinical referral sources. Collaboration terms require legal/compliance review."
        }
    if campaign in NONCLINICAL_CAMPAIGNS:
        amount = bonus_amount if bonus_amount is not None else "[APPROVED BONUS]"
        return {
          "eligible":True,
          "type":"promotional_partner_bonus",
          "copy":f"Eligible promotional partners may qualify for a {amount} referral/activation bonus, subject to Rescu approval, written terms, applicable law, and program rules."
        }
    return {"eligible":False,"type":"none","copy":""}
