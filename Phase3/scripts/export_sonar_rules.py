import os
import json
import requests

SONAR_URL = "http://localhost:9000"
TOKEN = os.environ["SONAR_TOKEN"]

OUTPUT_DIR = "rules/sonarqube"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_rules(language):
    page = 1
    page_size = 100
    all_rules = []

    while True:
        response = requests.get(
            f"{SONAR_URL}/api/rules/search",
            auth=(TOKEN, ""),
            params={
                "languages": language,
                "p": page,
                "ps": page_size,
            },
        )

        response.raise_for_status()

        data = response.json()

        rules = data.get("rules", [])
        total = data.get("total", 0)

        all_rules.extend(rules)

        print(
            f"{language}: "
            f"page {page} | "
            f"received {len(rules)} | "
            f"total collected {len(all_rules)}/{total}"
        )

        if not rules or len(all_rules) >= total:
            break

        page += 1

    return all_rules


for language in ["c", "cpp"]:

    rules = get_rules(language)

    output_file = os.path.join(
        OUTPUT_DIR,
        f"sonarqube-{language}-rules.json"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            rules,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nSaved {len(rules)} rules to {output_file}\n")
