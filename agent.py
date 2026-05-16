import json
import os
import pickle
from groq import Groq
from dotenv import load_dotenv
from retrieval import search
from prompts import SYSTEM_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ALWAYS_INCLUDE = {
    "Occupational Personality Questionnaire OPQ32r",
    "SHL Verify Interactive G+"
}

def get_valid_urls():
    from retrieval import get_catalog
    return {item["link"] for item in get_catalog()}

def build_catalog_context(messages: list) -> str:
    user_msgs = [m["content"] for m in messages if m["role"] == "user"]
    query = " ".join(user_msgs[-3:])
    results = search(query, top_k=15)

    result_names = {r["name"] for r in results}
    missing = ALWAYS_INCLUDE - result_names
    for name in missing:
        extras = search(name, top_k=3)
        for r in extras:
            if r["name"] == name:
                results.append(r)
                break

    lines = []
    for r in results:
        lines.append(
            f"Name: {r['name']}\n"
            f"URL: {r['url']}\n"
            f"Type: {r['test_type']}\n"
            f"Description: {r['description']}\n"
            f"Duration: {r['duration']}\n"
            f"Job Levels: {', '.join(r['job_levels'])}\n"
            f"Languages: {', '.join(r['languages'])}\n"
            f"---"
        )
    return "\n".join(lines)

def run_agent(messages: list) -> dict:
    if len(messages) >= 8:
        last_recs = []
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                try:
                    parsed = json.loads(msg["content"])
                    last_recs = parsed.get("recommendations", [])
                    break
                except:
                    break
        return {
            "reply": "We've reached the maximum conversation length. Here is your final shortlist.",
            "recommendations": last_recs,
            "end_of_conversation": True
        }

    catalog_context = build_catalog_context(messages)
    system = SYSTEM_PROMPT.replace("{catalog_context}", catalog_context)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}] + messages,
        temperature=0.2,
        max_tokens=1500
    )

    raw = response.choices[0].message.content.strip()

    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "reply": raw,
            "recommendations": [],
            "end_of_conversation": False
        }

    if result.get("recommendations"):
        valid_urls = get_valid_urls()
        result["recommendations"] = [
            r for r in result["recommendations"]
            if r.get("url") in valid_urls
        ]

    result.setdefault("reply", "")
    result.setdefault("recommendations", [])
    result.setdefault("end_of_conversation", False)

    return result