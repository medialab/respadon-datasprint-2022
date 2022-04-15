from collections import defaultdict
import csv
import os
from typing import Dict

THEMES_LIST = set(
    [
        "brevets",
        "eugenisme",
        "telethon",
        "adn",
        "FIV",
        "avortement",
        "chretien",
        "bioethique",
        "ogm",
        "bayer",
        "souches",
        "gene",
        "clonage",
        "genome",
        "embryon",
        "vache folle",
        "transgenique",
    ]
)


def get_themes_facets() -> Dict:

    terms = defaultdict(set)
    with open(
        os.path.join("themes_data", "terms-tfudf_election2002_harmonized-data.csv"), "r"
    ) as f:
        terms_csv = csv.DictReader(f)
        for term in terms_csv:
            if term["new_term"] in THEMES_LIST:
                terms[term["new_term"]].add(term["term"])
    return {
        theme: ("facet.query", f'text:({" OR ".join(sorted(list(ts)))})')
        for (theme, ts) in terms.items()
    }
