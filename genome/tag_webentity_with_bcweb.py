from collections import defaultdict
import os
import csv
import json
from ural.lru import LRUTrie
from ural import ensure_protocol

CORPUS_FILE = "génome élections 2002 v2 complet.json"
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
        new_tag = tag
        if tag["URL de départ"] in urls:
            new_tag = tag | urls[tag["URL de départ"]]
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

# tags from tf-idf analysis
with open(
    "domaine_theme.tags.csv",
    "r",
) as f:
    dr = csv.DictReader(f)
    for row in dr:
        domaine = ensure_protocol(row["domaine"])
        new_tag = {"tfidf": row["themes"]}
        if domaine in urls:
            new_tag = new_tag | urls[domaine]
        urls[domaine] = new_tag
        trie.set(domaine, new_tag)

themes_fields = set()
with open("domaine_theme.json", "r") as f:
    domaine_theme = json.load(f)
    for (domaine, themes) in domaine_theme.items():
        url = ensure_protocol(domaine)
        nb_page_total = 0
        for (theme, nb_page) in themes.items():
            nb_page_total += nb_page
            print(url, theme, nb_page)
            themes_fields.add(theme)
            new_tag = {theme: nb_page}
            if url in urls:
                new_tag = new_tag | urls[url]
            urls[url] = new_tag
            trie.set(url, new_tag)
        trie.set(url, {"total_tfidf": nb_page_total} | urls[url])

# on part d'un corpus hyphe
# pour chauque préfixe de WE on cherche un match dans l'arbre des tags
# fusionne des tags

output_data = defaultdict(dict)

fields = ["Thème", "candidat", "parti", "tfidf", "total_tfidf"] + list(themes_fields)

with open(os.path.join(DATA_PATH, CORPUS_FILE), "r") as webs_f:
    hyphe_incunable = json.load(webs_f)
    for web_entity in hyphe_incunable["webentities"]:
        for url in web_entity["PREFIXES AS URL"]:
            tag = trie.match(url)
            if tag:
                output_data[web_entity["ID"]]["name"] = web_entity["NAME"]
                existing_tags = output_data[web_entity["ID"]]
                for field in fields:
                    if field in tag:
                        if "field" in existing_tags:
                            existing_tags[field].add(tag[field])
                        else:
                            existing_tags[field] = {tag[field]}

print(f"{len(output_data.keys())} web entities with at least one tag")
with open(os.path.join(DATA_PATH, f"{CORPUS_FILE.split('.')[0]}.tags.csv"), "w") as f:
    writer = csv.DictWriter(f, ["web_entity_id", "name"] + fields)
    writer.writeheader()
    for (web_entity_id, values) in output_data.items():
        writer.writerow(
            {"web_entity_id": web_entity_id}
            | {
                k: "|".join((str(e) for e in v)) if isinstance(v, set) else str(v)
                for k, v in values.items()
            }
        )
