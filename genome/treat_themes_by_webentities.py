from collections import defaultdict
import json
import os
import csv
from textwrap import indent

from themes import get_themes_facets


THEME_PATH = "./themes_data/themes_web_entities"

themes_facets = get_themes_facets()

web_entity_themes = []

with open(os.path.join("hyphe_data", "genome_elections_2002.json"), "r") as f:
    hyphe = json.load(f)
    web_entity_names = {str(we["ID"]): we["NAME"] for we in hyphe["webentities"]}

for filename in os.listdir(THEME_PATH):
    with open(os.path.join(THEME_PATH, filename), "r") as f:
        web_entity_theme = {
            "web_entity_id": filename.split(".")[0],
            "name": web_entity_names[filename.split(".")[0]],
        }
        data = json.load(f)
        total_pages = data["response"]["numFound"]
        web_entity_theme["total_indexed_pages"] = total_pages
        web_entity_theme["indexed_in_solr"] = total_pages > 0
        for theme, (_, facet_query) in themes_facets.items():
            web_entity_theme[theme] = data["facet_counts"]["facet_queries"][facet_query]
            web_entity_theme[f"{theme}_binary"] = (
                data["facet_counts"]["facet_queries"][facet_query] > 0
            )

        web_entity_themes.append(web_entity_theme)

CSV_HEADERS = (
    ["web_entity_id", "name", "indexed_in_solr", "total_indexed_pages"]
    + list(themes_facets.keys())
    + [f"{theme}_binary" for theme in themes_facets.keys()]
)

with open("./hyphe_data/webentity_theme_raw.tags.csv", "w") as f:

    writer = csv.DictWriter(
        f,
        CSV_HEADERS,
    )
    writer.writeheader()
    writer.writerows(web_entity_themes)

with open("./hyphe_data/webentity_theme_per_1000.tags.csv", "w") as f:

    writer = csv.DictWriter(
        f,
        CSV_HEADERS,
    )
    writer.writeheader()
    # normalize thems weight by total pages which contains one theme
    writer.writerows(
        [
            {
                k: v
                if k not in themes_facets or not we["indexed_in_solr"]
                else 1000 * v / we["total_indexed_pages"]
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
