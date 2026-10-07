"""Revenue stack adapters: GrowthBook experiments, Mautic lifecycle, Twenty CRM.
Adapters only: no third-party source code is copied into Rescu Growth Engine.
"""
from dataclasses import dataclass, asdict
import os

@dataclass
class RevenueEvent:
    lead_id:str
    event:str
    campaign:str
    value:float=0
    owner:str=""
    source:str=""
    variant:str=""

def growthbook_config():
    return {
      "enabled": bool(os.getenv("GROWTHBOOK_CLIENT_KEY")),
      "client_key_env":"GROWTHBOOK_CLIENT_KEY",
      "experiments":[
        "homepage_primary_cta","hbot_partner_offer","ozone_offer",
        "trilift_offer","emsella_offer","google_meet_vs_whatsapp"
      ],
      "primary_metric":"qualified_booking",
      "revenue_metric":"collected_revenue"
    }

def mautic_config():
    return {
      "enabled": bool(os.getenv("MAUTIC_BASE_URL")),
      "base_url_env":"MAUTIC_BASE_URL",
      "segments":["new_lead","a_tier_partner","former_client","engaged_no_booking","booked","won","suppressed"],
      "rules":{
        "engaged_no_booking":"educational follow-up; stop on reply/booking/opt-out",
        "former_client":"reactivation sequence with service-specific offer",
        "suppressed":"never market"
      }
    }

def twenty_config():
    return {
      "enabled": bool(os.getenv("TWENTY_BASE_URL")),
      "base_url_env":"TWENTY_BASE_URL",
      "objects":["Organization","Contact","Opportunity","ReferralPartner","CampaignTouch"],
      "stages":["Discovered","Qualified","Drafted","Contacted","Replied","Meeting","Booked","Won","Lost"],
      "revenue_fields":["expected_value","collected_revenue","service_line","campaign","source","owner"]
    }

def event_payload(e:RevenueEvent): return asdict(e)
