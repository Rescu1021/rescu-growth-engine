from .scoring import Lead, score_lead, dedupe
from .npi import search, normalize
from .export import write_csv

NPI_CAMPAIGNS={
 "ortho_pt":["Physical Therapist","Orthopaedic Surgery","Sports Medicine"],
 "pelvic_floor":["Physical Therapist","Obstetrics & Gynecology","Urology"],
 "ozone_referral":["Internal Medicine","Family Medicine"]
}

def collect_npi(cities=("Scarsdale","Eastchester","Bronxville","Rye","Harrison"),state="NY",limit=25):
    leads=[]
    for campaign,taxonomies in NPI_CAMPAIGNS.items():
        for city in cities:
            for taxonomy in taxonomies:
                try: results=search(taxonomy_description=taxonomy,city=city,state=state,limit=limit)
                except Exception as e:
                    print("NPI error",city,taxonomy,e); continue
                for item in results:
                    row=normalize(item)
                    lead=Lead(**{k:row.get(k,"") for k in Lead.__dataclass_fields__ if k in row})
                    leads.append(score_lead(lead,campaign))
    return dedupe(leads)

def main():
    leads=sorted(collect_npi(),key=lambda x:x.score,reverse=True)
    path=write_csv(leads)
    print("Exported",len(leads),"leads to",path)
    for x in leads[:20]: print(x.tier,x.score,x.name,x.city,"->",x.service,x.owner)

if __name__=="__main__": main()
