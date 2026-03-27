# app/utils/json_utils.py

import json

def safe_json_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}