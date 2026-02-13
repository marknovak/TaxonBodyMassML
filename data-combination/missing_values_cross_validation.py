import pandas as pd
import requests

INPUT_CSV = "./data/BodyMass_with_full_taxonomy.csv"
OUTPUT_CSV = "./data/BodyMass_second_pass.csv"

GBIF_MATCH_URL = "https://api.gbif.org/v2/species/match"

# use starting index to start from the last saved index in case of interruption/failure
STARTING_INDEX = 0
MISSED_SPECIES_PATH = "./data/missed_species.txt"


def api_match(input_name):
    """
    gbif_match()
    inputs: input_name is a string which represents the scientific name of target species
    output: returns JSON response from fuzzy match API
    """
    params = {
        "scientificName": input_name,
    }
    r = requests.get(GBIF_MATCH_URL, params=params, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()


df = pd.read_csv(INPUT_CSV)

# these are the new columns that will be added to our dataset
taxonomy_fields = [
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species"
]

# temporary storage for any species which could not be found or
# resulted in error upon request to the API
missed_species = []

# iterate over each species and get its full taxonomy
for i, row in df.iterrows():
    missing_fields = []
    for field in taxonomy_fields:
        if row[field].isna():
            missing_fields.append(field)

    if len(missing_fields) == 0:
        continue
    
    # to prevent data loss, save results to csv every 100 iterations
    if i % 100 == 0:
        print("Saving from index:", i)
        df.to_csv(OUTPUT_CSV, index=False)

    # clean existing taxonomy data for request
    NAME = str(row["taxon"]).strip().replace("_", " ")
    if not NAME or NAME == "nan":
        continue

    try:
        result = api_match(NAME)
        print(NAME)
        # print(result)

        # store each classification to the dataframe
        classification = result.get("classification")
        for rank in classification:
            if rank in missing_fields:
                df.at[i, rank["rank"].lower()] = rank["name"]

    # upon failure, add the missed species to the record
    except FileNotFoundError as e:
        print(f"Failed on {NAME}: {e}")
        missed_species.append(NAME)
    except PermissionError:
        print("You do not have permission to read the file.")
        missed_species.append(NAME)

# final save of results to the output csv
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved: {OUTPUT_CSV}")

# write all missed species to the output txt
with open(MISSED_SPECIES_PATH, "w", encoding="utf-8") as missed_species_list:
    for species in missed_species:
        missed_species_list.write(species + "\n")
    print("Total missed species:", len(missed_species))
    print("List of missed species has been saved to:", MISSED_SPECIES_PATH)
