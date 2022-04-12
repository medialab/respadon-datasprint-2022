from collections import defaultdict
import os
import json
import csv
from urllib.parse import urlencode
from ural import normalize_url, force_protocol


CORPUS_FILE = "génome élections 2002 v2 complet.json"
THEMES_TERMS = ["ELECTIONS", "terms-tfudf_election2002_harmonized-data.csv"]
DATA_PATH = "bcweb_data"
SOLR_URL = "http://nemo10.bnf.fr:8983/solr/netarchivebuilder/select"


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

terms_facets = {"facet.query": [" OR ".join(ts) for (theme, ts) in terms.items()]}

curl_bash_script = []
all_queries = []

with open(os.path.join(DATA_PATH, CORPUS_FILE), "r") as webs_f:
    hyphe_incunable = json.load(webs_f)
    for web_entity in hyphe_incunable["webentities"]:
        # using filter looks like an optimization but not sure...
        prefix_normalize = set(
            [
                # mimic wayback url nomralization https://github.com/netarchivesuite/solrwayback/blob/master/src/bundle/solrconfig_7.7.3/solr/configsets/netarchivebuilder/conf/schema.xml#L157
                force_protocol(
                    normalize_url(
                        url, strip_irrelevant_subdomains=True, strip_trailing_slash=True
                    ),
                    protocol="http",
                )
                for url in web_entity["PREFIXES AS URL"]
            ]
        )
        prefixes_filters = [f'url_search:"{url}"*' for url in prefix_normalize]
        if len(prefixes_filters) > 0:

            query_string = urlencode(
                {"q": " OR ".join(prefixes_filters)} | terms_facets
            )

            query = f"{SOLR_URL}?{query_string}"
            all_queries.append(query)
            curl_bash_script.append(f"curl '{query}' > {web_entity['ID']}.json")
        else:
            print(
                f'missing http without www prefix in {web_entity["NAME"]} {web_entity["PREFIXES AS URL"]}'
            )
with open(
    os.path.join(DATA_PATH, "solr_webentities_themes_search_bodies.json"), "w"
) as f:
    json.dump(all_queries, f, indent=2)
with open(os.path.join(DATA_PATH, "solr_webentities_themes_curl.sh"), "w") as f:
    f.write("\n".join(curl_bash_script))
