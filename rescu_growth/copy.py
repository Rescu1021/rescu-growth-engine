from .offers import offer_for

def subject(lead):
    return "{} x Rescu — a local partnership idea".format(lead.name)

def email_body(lead,contact_name=""):
    o=offer_for(lead.campaign)
    hello="Hi {},".format(contact_name) if contact_name else "Hi there,"
    bullets="\n".join("• "+x for x in o["stack"])
    return """{hello}

I'm Dr. Randy Taylor, founder of Rescu Wellness in Scarsdale.

{hook}

Instead of asking your team to build another service line, the idea is simple: keep doing what you do best and use Rescu as a local extension when the fit is appropriate.

{name}:
{bullets}

No complicated rollout. We can start with a small pilot, see whether your members or clients actually use it, and expand only if it earns its place.

{cta}

Dr. Randy Taylor
Rescu Wellness
111 Brook Street, Scarsdale, NY
Rescu.life
914-281-4876

Commercial partnership outreach from Rescu Wellness. If you'd rather not receive messages like this, reply OPT OUT.""".format(hello=hello,hook=o["hook"],name=o["name"],bullets=bullets,cta=o["cta"])

def followup_body(lead,contact_name=""):
    o=offer_for(lead.campaign)
    hello="Hi {},".format(contact_name) if contact_name else "Hi there,"
    return """{hello}

Quick follow-up on the Rescu partnership idea.

The goal isn't to add work for your team. It's to give you a local option you can use when appropriate, with Rescu handling the scheduling and experience.

{cta}

If it's not relevant, just reply OPT OUT and I'll close the loop.

Dr. Randy Taylor
Rescu Wellness | Scarsdale
914-281-4876""".format(hello=hello,cta=o["cta"])
