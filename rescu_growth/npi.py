"""CMS NPI Registry connector (public provider data)."""
import json, urllib.parse, urllib.request

BASE="https://npiregistry.cms.hhs.gov/api/"

def search(first_name="", last_name="", taxonomy_description="", city="", state="NY", limit=50):
    params={"version":"2.1","limit":min(limit,200)}
    for k,v in {
        "first_name":first_name,"last_name":last_name,
        "taxonomy_description":taxonomy_description,"city":city,"state":state
    }.items():
        if v: params[k]=v
    url=BASE+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"RescuGrowthEngine/0.2"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r).get("results",[])

def normalize(result):
    basic=result.get("basic",{})
    addresses=result.get("addresses",[])
    loc=next((a for a in addresses if a.get("address_purpose")=="LOCATION"), addresses[0] if addresses else {})
    tax=result.get("taxonomies",[])
    primary=next((t for t in tax if t.get("primary")), tax[0] if tax else {})
    name=basic.get("organization_name") or " ".join(x for x in [basic.get("first_name",""),basic.get("last_name","")] if x)
    return {
      "name":name,"category":primary.get("desc",""),"city":loc.get("city","").title(),
      "state":loc.get("state",""),"phone":loc.get("telephone_number",""),
      "website":"","source":"CMS NPI","npi":result.get("number","")
    }
