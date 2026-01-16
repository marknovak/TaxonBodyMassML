import pandas as pd
import requests
import time

INPUT_CSV = "./data/BodyMass.csv"
OUTPUT_CSV = "./data/BodyMass_with_full_taxonomy.csv"

GBIF_MATCH_URL = "https://api.gbif.org/v2/species/match"

STARTING_INDEX = 0

def gbif_match(name):
    params = {
        "scientificName": name,
    }
    r = requests.get(GBIF_MATCH_URL, params=params, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()

df = pd.read_csv(INPUT_CSV)

taxonomy_fields = [
    "kingdom", "phylum", "class", "order",
    "family", "genus", "species", "confidence"
]

for field in taxonomy_fields:
    if field not in df.columns:
        df[field] = None

for i, row in df.iterrows():
    if i < STARTING_INDEX: 
        print("skipped:", i)
        continue
    if i % 100 == 0:
        print("Saving from index:", i)
        df.to_csv(OUTPUT_CSV, index=False)
        
    name = str(row["taxon"]).strip()
    if not name or name == "nan":
        continue

    try:
        name = name.replace("_", " ")
        result = gbif_match(name)
        print(name)
        #print(result)

        classification = result.get("classification")
        for rank in classification:
            df.at[i, rank["rank"].lower()] = rank["name"]
        
        diagnostics = result.get("diagnostics")
        df.at[i, "confidence"] = diagnostics["confidence"]

    except Exception as e:
        print(f"Failed on {name}: {e}")

df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved: {OUTPUT_CSV}")
