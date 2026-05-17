import json
import re
from pathlib import Path

CATALOG_PATH = Path("data/catalog/shl_product_catalog.json")


def clean_json_string(content):
    """
    Removes invalid control characters from JSON.
    """

    # Remove invalid ASCII control chars
    content = re.sub(r'[\x00-\x1F\x7F]', '', content)

    return content


def load_catalog():

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        raw_content = f.read()

    cleaned_content = clean_json_string(raw_content)

    data = json.loads(cleaned_content)

    return data


if __name__ == "__main__":

    catalog = load_catalog()

    print(f"\nLoaded {len(catalog)} assessments\n")

    print("Top-level type:", type(catalog))

    print("\nSample Assessment:\n")

    if isinstance(catalog, list):
        print(json.dumps(catalog[0], indent=2)[:3000])

    elif isinstance(catalog, dict):

        first_key = list(catalog.keys())[0]

        print("Top Keys:", list(catalog.keys()))

        print("\nFirst Item:\n")

        print(json.dumps(catalog[first_key], indent=2)[:3000])