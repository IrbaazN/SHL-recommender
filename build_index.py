import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

print("Loading catalog...")
with open("catalog.json") as f:
    catalog = json.load(f)
print(f"Total assessments: {len(catalog)}")

def build_text(item):
    parts = []
    parts.append(item.get("name", ""))
    parts.append(item.get("description", ""))
    parts.append("Test types: " + ", ".join(item.get("keys", [])))
    parts.append("Job levels: " + ", ".join(item.get("job_levels", [])))
    parts.append("Languages: " + ", ".join(item.get("languages", [])))
    if item.get("remote") == "yes":
        parts.append("Remote testing available")
    if item.get("adaptive") == "yes":
        parts.append("Adaptive testing")
    if item.get("duration"):
        parts.append("Duration: " + item["duration"])
    return " | ".join(parts)

texts = [build_text(item) for item in catalog]

print("Loading embedding model...")
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, batch_size=16)
embeddings = np.array(embeddings).astype("float32")
faiss.normalize_L2(embeddings)

print("Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(index, "embeddings/catalog.index")
with open("embeddings/catalog_meta.pkl", "wb") as f:
    pickle.dump(catalog, f)

print(f"Done! Saved {index.ntotal} vectors.")