import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify

df = pd.read_csv("./data/BodyMass.csv")
print(df)

df = df.dropna()
print(df)

taxon = df["taxon"].to_list()
for i in range(len(taxon)):
    #print(taxon[i])
    for j in range(len(taxon[i])):
        if taxon[i][j] == "_":
            taxon[i] = taxon[i][j+1:]
            #print(taxon[i])
            break
        
df["species_name"] = taxon

print(df)

app = Flask(__name__)

@app.route('/single_species', methods=['GET'])
def single_species():
    species_name = request.args.get('species_name')
    
    if not species_name:
        return jsonify({"error": "Missing 'species_name' parameter"}), 400
    
    row = df[df["species_name"] == species_name]
    
    if row.empty:
        return jsonify({"error": f"Species '{species_name}' not found"}), 404
    
    species_mass = row.iloc[0]["mass_g"]
    
    return jsonify({
        "species_name": species_name,
        "mass_g": species_mass
    })

if __name__ == '__main__':
        app.run(debug=True)