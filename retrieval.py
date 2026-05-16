import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
index = faiss.read_index("embeddings/catalog.index")

with open("embeddings/catalog_meta.pkl", "rb") as f:
    catalog = pickle.load(f)

KEY_TO_TYPE = {
    "Ability & Aptitude": "A",
    "Assessment Exercises": "E",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S"
}

def search(query: str, top_k: int = 10) -> list:
    query_vec = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        item = catalog[idx]
        type_letters = list(set(
            KEY_TO_TYPE.get(k, "K") for k in item.get("keys", [])
        ))
        results.append({
            "name": item["name"],
            "url": item["link"],
            "test_type": ",".join(sorted(type_letters)),
            "description": item.get("description", ""),
            "duration": item.get("duration", ""),
            "job_levels": item.get("job_levels", []),
            "languages": item.get("languages", []),
            "remote": item.get("remote", ""),
            "adaptive": item.get("adaptive", ""),
            "score": float(score)
        })
    return results

if __name__ == "__main__":
    results = search("Java developer mid-level")
    for r in results:
        print(f"{r['name']} ({r['test_type']}) — {r['score']:.3f}")