from collections import defaultdict
import os
import json
import csv
from urllib.parse import urlencode
from ural import normalize_url, force_protocol

from themes import get_themes_facets

CORPUS_PATH = os.path.join("hyphe_data", "genom2002_mercredi13-04.json")
THEMES_DATA_PATH = "themes_data"
SOLR_URL = "http://nemo10.bnf.fr:8983/solr/netarchivebuilder/select"

terms_facets_dict = get_themes_facets()
terms_facets = list(terms_facets_dict.values())

curl_bash_script = []
all_queries = []

with open(CORPUS_PATH, "r") as webs_f:
    hyphe = json.load(webs_f)
    for web_entity in hyphe["webentities"]:
        if web_entity["STATUS"] in ["IN", "UNDECIDED"]:
            # using filter looks like an optimization but not sure...
            prefix_normalize = set(
                [
                    # mimic wayback url nomralization https://github.com/netarchivesuite/solrwayback/blob/master/src/bundle/solrconfig_7.7.3/solr/configsets/netarchivebuilder/conf/schema.xml#L157
                    force_protocol(
                        normalize_url(
                            url,
                            strip_irrelevant_subdomains=True,
                            strip_trailing_slash=True,
                        ),
                        protocol="http",
                    )
                    for url in web_entity["PREFIXES AS URL"]
                ]
            )
            prefixes_filters = [f'url_search:"{url}"*' for url in prefix_normalize]
            if len(prefixes_filters) > 0:

                query_o = [
                    ("rows", 0),
                    ("facet", "on"),
                    ("q", " OR ".join(prefixes_filters)),
                ] + terms_facets
                query_string = urlencode(query_o)

                query = f"{SOLR_URL}?{query_string}"
                all_queries.append(query)
                curl_bash_script.append(f"curl '{query}' > {web_entity['ID']}.json")
            else:
                print(
                    f'missing http without www prefix in {web_entity["NAME"]} {web_entity["PREFIXES AS URL"]}'
                )
with open(
    os.path.join(THEMES_DATA_PATH, "solr_webentities_themes_search_bodies.json"), "w"
) as f:
    json.dump(all_queries, f, indent=2)
with open(os.path.join(THEMES_DATA_PATH, "solr_webentities_themes_curl.sh"), "w") as f:
    f.write(";\n".join(curl_bash_script))
