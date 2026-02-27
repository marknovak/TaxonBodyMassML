import pandas as pd
import requests
import time

import xml.etree.ElementTree as ET

INPUT_CSV = "./data/BodyMass_with_full_taxonomy.csv"
OUTPUT_CSV = "./data/BodyMass_second_pass.csv"

STARTING_INDEX = 0
MISSED_SPECIES_PATH = "./data/missed_species_2.txt"

NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def ncbi_match(input_name):
    """
    Get taxonomy lineage from NCBI
    """

    params = {
        "db": "taxonomy",
        "term": input_name,
        "retmode": "json"
    }

    r = requests.get(NCBI_ESEARCH, params=params, timeout=10)

    if r.status_code != 200:
        return {}

    data = r.json()

    id_list = data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return {}

    tax_id = id_list[0]

    params = {
        "db": "taxonomy",
        "id": tax_id,
        "retmode": "xml"
    }

    r = requests.get(NCBI_EFETCH, params=params, timeout=10)

    if r.status_code != 200:
        return {}

    return r.text


def parse_ncbi_xml(xml_text):
    

    taxonomy = {}

    root = ET.fromstring(xml_text)

    lineage = root.find(".//LineageEx")

    if lineage is not None:
        for taxon in lineage.findall("Taxon"):

            rank = taxon.find("Rank").text.lower()
            name = taxon.find("ScientificName").text

            taxonomy[rank] = name

    species = root.find(".//ScientificName")
    if species is not None:
        taxonomy["species"] = species.text

    return taxonomy


df = pd.read_csv(INPUT_CSV)

taxonomy_fields = [
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species"
]

missed_species = []


for i, row in df.iterrows():

    if i < STARTING_INDEX:
        continue

    missing_fields = [
        field for field in taxonomy_fields
        if pd.isna(row[field])
    ]

    if not missing_fields:
        continue

    if i % 100 == 0:
        print("Saving from index:", i)
        df.to_csv(OUTPUT_CSV, index=False)

    NAME = str(row["taxon"]).strip().replace("_", " ")

    if not NAME or NAME == "nan":
        continue

    try:

        print("Query:", NAME)

        xml_result = ncbi_match(NAME)

        if not xml_result:
            missed_species.append(NAME)
            continue

        taxonomy = parse_ncbi_xml(xml_result)

        for field in missing_fields:
            if field in taxonomy:
                df.at[i, field] = taxonomy[field]

        time.sleep(0.34)

    except Exception as e:

        print("Failed:", NAME, e)
        missed_species.append(NAME)


df.to_csv(OUTPUT_CSV, index=False)

print("Saved:", OUTPUT_CSV)


with open(MISSED_SPECIES_PATH, "w", encoding="utf-8") as f:

    for species in missed_species:
        f.write(species + "\n")

print("Missed:", len(missed_species))