# fix_catalog.py - replace with this
import json
import re

with open("catalog.json", "rb") as f:
    raw = f.read()

text = raw.decode("utf-8", errors="ignore")

# Remove control characters inside JSON strings
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

# Fix literal newlines inside string values
text = re.sub(r'(?<=")([^"]*)\n([^"]*?)(?=")', r'\1 \2', text)

try:
    data = json.loads(text)
    print(f"Parsed successfully: {len(data)} assessments")
    with open("catalog.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved clean catalog.json")
except json.JSONDecodeError as e:
    print(f"Still failing: {e}")
    pos = e.pos
    print(repr(text[pos-50:pos+50]))