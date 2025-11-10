"""
prototype_lookup.py
-------------------
Provides API endpoints for prototype lookup operations in the web development module.
single_species endpoint receives an input of 
"""
import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# read the raw bodymass data into a dataframe
df = pd.read_csv("./data/BodyMass.csv")
print(df)


# print and remove any data with missing values
print("Number of missing values in each column:\n", df.isna().sum())
df = df.dropna()
print(df)

# save taxon column as a list and parse it such that it's only the species name
taxon = df["taxon"].to_list()
for i in range(len(taxon)):
    # print(taxon[i])
    for j in range(len(taxon[i])):
        if taxon[i][j] == "_":
            taxon[i] = taxon[i][j + 1 :]
            # print(taxon[i])
            break
# save this updated list as a new column
df["species_name"] = taxon

print(df)



@app.route("/single_species", methods=["GET"])
def single_species():
    """
    single_species()
    -------------------
    receive a request for a mass of a single species from webapp backend
    """
    species_name = request.args.get("species_name")

    # if there is no input species name, then return an error
    if not species_name:
        return jsonify({"error": "Missing 'species_name' parameter"}), 400

    # filter for a row in the database which matches this species name exactly
    row = df[df["species_name"] == species_name]

    # if nothing matched, return a not found error
    if row.empty:
        return jsonify({"error": f"Species '{species_name}' not found"}), 404

    # isolate the mass from the species row
    species_mass = row.iloc[0]["mass_g"]

    # return a json object with the species name and mass
    return jsonify({"species_name": species_name, "mass_g": species_mass})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
