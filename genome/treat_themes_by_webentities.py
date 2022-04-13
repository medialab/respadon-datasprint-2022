from collections import defaultdict
import json
import os
import csv
from textwrap import indent

from themes import get_themes_facets


THEME_PATH = "./themes_data/themes_web_entities"

themes_facets = get_themes_facets()

web_entity_themes = []

for filename in os.listdir(THEME_PATH):
    with open(os.path.join(THEME_PATH, filename), "r") as f:
        web_entity_theme = {"web_entity_id": filename.split(".")[0]}
        data = json.load(f)
        total_pages = data["response"]["numFound"]
        web_entity_theme["total_themes_pages"] = total_pages
        for theme, (_, facet_query) in themes_facets.items():
            web_entity_theme[theme] = data["facet_counts"]["facet_queries"][facet_query]

        web_entity_themes.append(web_entity_theme)


with open("./hyphe_data/webentity_theme_raw.tags.csv", "w") as f:

    writer = csv.DictWriter(
        f, ["web_entity_id", "total_themes_pages"] + list(themes_facets.keys())
    )
    writer.writeheader()
    writer.writerows(web_entity_themes)

with open("./hyphe_data/webentity_theme_per_1000.tags.csv", "w") as f:

    writer = csv.DictWriter(
        f, ["web_entity_id", "total_themes_pages"] + list(themes_facets.keys())
    )
    writer.writeheader()
    # normalize thems weight by total pages which contains one theme
    writer.writerows(
        [
            {
                k: v if k not in themes_facets else 1000 * v / we["total_themes_pages"]
                for (k, v) in we.items()
            }
            for we in web_entity_themes
        ]
    )

    # print(list(zip(domains_number, domains_number[1:])))
    # for (domain, number) in zip(domains_number, domains_number[1:]):
    #     print([theme, domain, number])
    # tags = csv.DictReader(f, dialect="tsv")
    # for tag in tags:
    #     if not tag["URL de départ"] in urls:
    #         trie.set(tag["URL de départ"], tag)
    #     else:
    #         tag = tag | urls[tag["URL de départ"]]
    #     urls[tag["URL de départ"]] = tag
