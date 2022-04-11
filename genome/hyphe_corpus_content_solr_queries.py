from collections import defaultdict
import os
import json
import csv

CORPUS_FILE = "génome élections 2002 v2 complet.json"
THEMES_TERMS = ["ELECTIONS", "terms-tfudf_election2002_harmonized-data.csv"]
DATA_PATH = "bcweb_data"
SOLR_URL = "http://nemo10.bnf.fr:8983/solr/netarchivebuilder/query"


themes_list = set(
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
terms = defaultdict(set)
with open(os.path.join(DATA_PATH, *THEMES_TERMS), "r") as f:
    terms_csv = csv.DictReader(f)
    for term in terms_csv:
        if term["new_term"] in themes_list:
            terms[term["new_term"]].add(term["term"])

terms_facets = {
    theme: {"type": "query", "q": f'text:{" OR ".join(ts)}'}
    for (theme, ts) in terms.items()
}

curl_bash_script = []
all_bodies = []

with open(os.path.join(DATA_PATH, CORPUS_FILE), "r") as webs_f:
    hyphe_incunable = json.load(webs_f)
    for web_entity in hyphe_incunable["webentities"]:
        # using filter looks like an optimization but not sure...
        prefixes_filters = [
            f"filter(url:{url}*)" for url in web_entity["PREFIXES AS URL"]
        ]
        search_query_body = {
            "query": " OR ".join(prefixes_filters),
            "facet": terms_facets,
        }
        curl_bash_script.append(
            f"curl {SOLR_URL} -d '{json.dumps(search_query_body)}'' > {web_entity['ID']}.json"
        )
        all_bodies.append(search_query_body)

with open(
    os.path.join(DATA_PATH, "solr_webentities_themes_search_bodies.json"), "w"
) as f:
    json.dump(all_bodies, f, indent=2)
with open(os.path.join(DATA_PATH, "solr_webentities_themes_curl.sh"), "w") as f:
    f.write("\n".join(curl_bash_script))
