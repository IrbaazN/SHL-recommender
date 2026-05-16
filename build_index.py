import json
import os

print("Loading catalog...")
with open("catalog.json") as f:
    catalog = json.load(f)
print(f"Total assessments: {len(catalog)}")

os.makedirs("embeddings", exist_ok=True)

with open("embeddings/catalog_meta.json", "w") as f:
    json.dump(catalog, f)

print("Done! Saved catalog.")