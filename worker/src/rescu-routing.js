// Rescu commercial lead routing. No patient data and no outbound sends.
export function routeLead({ campaign = "", service = "", tags = [] } = {}) {
  const haystack = [campaign, service, ...tags].join(" ").toLowerCase();
  const clinical = /ozone_referral|clinical_review|medical referral|physician review/.test(haystack);
  if (clinical) return { routingOwner: "CLINICAL_REVIEW", automationState: "ESCALATE" };
  if (/trilift|aesthetic|facial|microneedling|ipl|laser hair/.test(haystack))
    return { routingOwner: "ANA", automationState: "REVIEW_REQUIRED" };
  if (/hbot|hyperbaric|performance|fitness|ortho_pt|sports|corporate|clubs|pelvic_floor/.test(haystack))
    return { routingOwner: "MYRNA", automationState: "REVIEW_REQUIRED" };
  return { routingOwner: "REVIEW", automationState: "REVIEW_REQUIRED" };
}
