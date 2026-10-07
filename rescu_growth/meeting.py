"""Meeting CTA helpers. Configure a real scheduling URL before outbound use."""
import os
def meeting_url():
    return os.getenv("RESCU_MEETING_URL","").strip()

def meeting_cta():
    url=meeting_url()
    if url:
        return f"Prefer to talk it through? Choose a 15-minute Google Meet: {url}"
    return "Prefer to talk it through? Reply MEET and we'll send you options for a 15-minute Google Meet."
