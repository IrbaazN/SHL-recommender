import json
import os

_catalog = None

def get_catalog():
    global _catalog
    if _catalog is None:
        with open("embeddings/catalog_meta.json") as f:
            _catalog = json.load(f)
    return _catalog

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

def score_item(item, query_words):
    text = " ".join([
        item.get("name", ""),
        item.get("description", ""),
        " ".join(item.get("keys", [])),
        " ".join(item.get("job_levels", [])),
        " ".join(item.get("languages", []))
    ]).lower()
    return sum(1 for w in query_words if w in text)

def search(query: str, top_k: int = 10) -> list:
    catalog = get_catalog()
    query_words = [w for w in query.lower().split() if len(w) > 2]

    scored = []
    for item in catalog:
        score = score_item(item, query_words)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results = []
    for score, item in top:
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