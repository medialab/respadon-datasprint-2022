from collections import defaultdict
import json
import os
import csv
from textwrap import indent


THEME_PATH = "thème_par_domaine"

domain_theme = defaultdict(dict)

for filename in os.listdir(THEME_PATH):
    with open(os.path.join(THEME_PATH, filename), "r") as f:
        theme = filename.split(".")[0]
        data = json.load(f)
        print(theme)
        domains_number = data["facet_counts"]["facet_fields"]["domain"]
        for i in range(0, int(len(domains_number)), 2):
            (domain, number) = domains_number[i : i + 2]
            domain_theme[domain][theme] = number

with open("domaine_theme.json", "w") as f:
    json.dump(domain_theme, f, indent=2)

with open("domaine_theme.tags.csv", "w") as f:

    writer = csv.DictWriter(f, ["domaine", "themes"])
    writer.writeheader()
    for domain, themes in domain_theme.items():
        writer.writerow({"domaine": domain, "themes": "|".join(themes.keys())})

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
