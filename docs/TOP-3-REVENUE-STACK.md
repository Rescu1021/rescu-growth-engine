# Top 3 Revenue Stack for Rescu

Goal: build infrastructure capable of materially increasing qualified demand, conversion and retention. No software can guarantee 3x revenue.

## 1 — GrowthBook: Conversion Intelligence
Use GrowthBook via its public SDK/API, not by copying its repository into Rescu.

Initial experiments:
- Homepage CTA: Explore My Options vs Build My Rescu Plan
- Google Meet vs WhatsApp as secondary close
- HBOT athlete partnership hero/value stack
- Ozone consultation positioning
- TriLift trial positioning
- Emsella consultation/offer positioning

North-star metrics:
- qualified_booking
- consultation_request
- partner_meeting
- collected_revenue

Rule: do not optimize for clicks alone.

## 2 — Mautic: Lifecycle + Reactivation
Integrate as an external marketing automation service/API.

Segments:
- New lead
- A-tier partner
- Former client
- Engaged but not booked
- Booked
- Won
- Suppressed

Sequences:
- 0/2/5-day lead nurture
- former-client reactivation
- no-show recovery
- partner follow-up
- post-visit cross-service education

Respect consent, suppression, opt-outs and applicable messaging/email rules.

## 3 — Twenty: Revenue CRM
Integrate through Twenty APIs/webhooks or the permissively licensed SDK path rather than copying/modifying the full AGPL application.

Objects:
- Organization
- Contact
- Opportunity
- Referral Partner
- Campaign Touch

Pipeline:
Discovered -> Qualified -> Drafted -> Contacted -> Replied -> Meeting -> Booked -> Won/Lost

Every Won record stores service line, source, campaign and collected revenue so Growth Engine can learn which lead categories and offers actually make money.

## Closed loop
Growth Engine -> target
Creative/Funnel Engine -> offer
GrowthBook -> experiment
Mautic -> nurture/reactivate
Twenty -> opportunity/revenue truth
Growth Engine -> re-score based on revenue

## Rollout order
1. Instrument revenue events and GrowthBook experiment IDs.
2. Connect CRM objects and opportunity stages.
3. Add lifecycle sequences only after suppression/consent rules are verified.
4. Scale winning offer/creative combinations.
