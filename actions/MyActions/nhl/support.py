import json


def write_data_to_json(data, filename):
    with open(f"data/{filename}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
