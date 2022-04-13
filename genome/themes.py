from collections import defaultdict
import csv
import os
from typing import Dict

THEMES_TERMS = ["ELECTIONS", "terms-tfudf_election2002_harmonized-data.csv"]
DATA_PATH = "bcweb_data"
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
        "genes",
        "clonage",
        "genome",
        "embryon",
        "vache_folle",
        "transgenetique",
    ]
)


def get_themes_facets() -> Dict:

    terms = defaultdict(set)
    with open(os.path.join(DATA_PATH, *THEMES_TERMS), "r") as f:
        terms_csv = csv.DictReader(f)
        for term in terms_csv:
            if term["new_term"] in THEMES_LIST:
                terms[term["new_term"]].add(term["term"])
    return {
        theme: ("facet.query", f'text:({" OR ".join(sorted(list(ts)))})')
        for (theme, ts) in terms.items()
    }
