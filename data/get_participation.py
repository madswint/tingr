import pandas as pd
import requests

# when new politicians are added to the project, the dictionary below must be updated with aktoer_id from  matched with politikerid, 
# and this script must be run to populate the politiker table with an 'deltagelsesprocent' attribute.

AKTOER_MAP = {
    1: 145,
    2: 15777,
    3: 138,
    4: 18703,
    5: 43, 
    6: 18724,
    7: 238,
    9: 20351,
    10: 15770, 
    11: 152, 
    12: 18691,
    13: 206,
    14: 21362,
    15: 244, 
    16: 182,
    17: 18713,
    18: 18723,
    19: 141,
    20: 15776,
    21: 57,
    
}

results = {}

def get_count(filter_str):          # uses the requests library , converts the API's JSON "response object" to a python dictionary, and returns the value as an int
    url = f"https://oda.ft.dk/api/Stemme?$inlinecount=allpages&$top=1&$filter={filter_str}"
    r = requests.get(url, headers={"Accept": "application/json"})   
    return int(r.json()["odata.count"])     


for pol_id, ft_id in AKTOER_MAP.items():
    total  = get_count(f"aktørid eq {ft_id}")
    absent = get_count(f"aktørid eq {ft_id} and typeid eq 3")
    voted  = total - absent
    pct    = (voted / total * 100) if total > 0 else None
    results[pol_id] = pct
    print(f"politikerid {pol_id}: {pct}%")


df = pd.read_csv("politiker.csv", sep=";", encoding="utf-8-sig")
df["deltagelsesprocent"] = df["politikerid"].map(results)

df = df.dropna(subset=["politikerid"])
df["politikerid"] = df["politikerid"].astype(int)
df = df.dropna(subset=["partiid"])
df["partiid"] = df["partiid"].astype(int)

df.to_csv("politiker.csv", sep=";", index=False, encoding="utf-8-sig")
print("Saved to politiker.csv")



