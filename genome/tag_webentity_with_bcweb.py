from collections import defaultdict
import os
import csv
import json
from ural.lru import LRUTrie
from ural import ensure_protocol

from themes import THEMES_LIST

CORPUS_FILE = "genome_elections_2002.json"
# CORPUS_FILE = "génome incunable.json"

DATA_PATH = "bcweb_data"
GENOME_PATH = os.path.join(DATA_PATH, "GENOME")

csv.register_dialect("tsv", delimiter=";")


# créer un arbre d'URL à partir des données BCWeb
# URL de départ de BCEB => TAGs
trie = LRUTrie()
urls = {}
# BCWEB
for filename in os.listdir(GENOME_PATH):
    with open(os.path.join(GENOME_PATH, filename), "r") as f:

        tags = csv.DictReader(f, dialect="tsv")
        for tag in tags:
            new_tag = tag
            if tag["URL de départ"] in urls:
                new_tag = tag | urls[tag["URL de départ"]]
            urls[tag["URL de départ"]] = new_tag
            trie.set(tag["URL de départ"], new_tag)
# Elections 2004
with open(
    os.path.join(DATA_PATH, "ELECTIONS", "Data_elections_bnf_2004.csv"), "r"
) as f:
    tags = csv.DictReader(f, dialect="tsv")
    for tag in tags:
        new_tag = {
            "Thème": tag["Typologie"],
            "parti": tag["Parti"],
            "candidat": tag["Candidat"],
        }
        if tag["URL de départ"] in urls:
            new_tag = new_tag | urls[tag["URL de départ"]]
        urls[tag["URL de départ"]] = new_tag
        trie.set(tag["URL de départ"], new_tag)

# special tags for 2002
with open(
    os.path.join(DATA_PATH, "ELECTIONS", "domaines-etiquettes-1996-2004.json"), "r"
) as f:
    politique = json.load(f)
    for tag in politique:
        new_tag = {}
        if "candidat" in tag:
            new_tag["candidat"] = tag["candidat"]
        if "category" in tag:
            new_tag["Thème"] = tag["category"].split("/")[0].strip()
        url = ensure_protocol(tag["domain"])
        if url in urls:
            new_tag = new_tag | urls[url]
        urls[url] = new_tag
        trie.set(url, new_tag)


# on part d'un corpus hyphe
# pour chauque préfixe de WE on cherche un match dans l'arbre des tags
# fusionne des tags

output_data = defaultdict(dict)

fields = ["Thème", "candidat", "parti"]

# prepare themes tags
# themes tags
themes_tags = defaultdict(dict)
if os.path.exists("./hyphe_data/webentity_theme_per_1000.tags.csv"):

    with open("./hyphe_data/webentity_theme_per_1000.tags.csv", "r") as f:
        themes_by_web_entities = csv.DictReader(f)
        fields += ["one_genome_theme"] + [
            f
            for f in themes_by_web_entities.fieldnames
            if f not in ["web_entity_id", "name"]
        ]

        for themes_data in themes_by_web_entities:
            for k, v in themes_data.items():
                if k not in ["web_entity_id", "name"]:
                    themes_tags[int(themes_data["web_entity_id"])][k] = v
                if "binary" in k and v == "True":
                    themes_tags[int(themes_data["web_entity_id"])][
                        "one_genome_theme"
                    ] = "True"

with open(os.path.join("hyphe_data", CORPUS_FILE), "r") as webs_f:
    hyphe = json.load(webs_f)
    for web_entity in hyphe["webentities"]:
        if web_entity["ID"] in output_data:
            existing_tags = output_data[web_entity["ID"]]
        else:
            existing_tags = {}
        for url in web_entity["PREFIXES AS URL"]:
            tag = trie.match(url)
            if tag:
                for field in fields:
                    if field in tag:
                        if "field" in existing_tags:
                            existing_tags[field].add(tag[field])
                        else:
                            existing_tags[field] = {tag[field]}
        # add themes tags only for web entities which has been indexed in SOLR
        if (
            web_entity["ID"] in themes_tags
            and themes_tags[web_entity["ID"]]["indexed_in_solr"] == "True"
        ):
            existing_tags = existing_tags | themes_tags[web_entity["ID"]]
        if len(existing_tags.keys()) > 0:
            existing_tags["name"] = web_entity["NAME"]
            output_data[web_entity["ID"]] = existing_tags


print(f"{len(output_data.keys())} web entities with at least one tag")
with open(f"./hyphe_data/{CORPUS_FILE.split('.')[0]}.tags.csv", "w") as f:
    writer = csv.DictWriter(f, ["web_entity_id", "name", "total_themes_pages"] + fields)
    writer.writeheader()
    for (web_entity_id, values) in output_data.items():

        writer.writerow(
            {"web_entity_id": web_entity_id}
            | {
                k: "|".join((str(e) for e in v)) if isinstance(v, set) else str(v)
                for k, v in values.items()
            }
        )
