from collections import defaultdict
import json
import csv

out_data = []
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
total_theme_values = defaultdict(int)
total_domain_values = defaultdict(int)
with open("domaine_theme.json", "r") as f:
    in_data = json.load(f)
    for (domain, themes) in in_data.items():
        themes_with_0 = themes
        for t in themes:
            if t not in themes_with_0:
                themes_with_0[t] = 0
        for (theme, value) in themes_with_0.items():
            total_theme_values[theme] += value
            total_domain_values[domain] += value
            out_data.append({"domaine": domain, "theme": theme, "value": value})

with open("domaine_theme_viz.csv", "w") as f:
    w = csv.DictWriter(f, ["domaine", "theme", "value"])
    w.writeheader()
    w.writerows(out_data)

with open("nodes.csv", "w") as f:
    w = csv.DictWriter(f, ["Id", "type", "total"])
    w.writeheader()
    w.writerows(
        [{"Id": t, "type": "theme", "total": v} for t, v in total_theme_values.items()]
    )
    w.writerows(
        [
            {"Id": t, "type": "domaine", "total": v}
            for t, v in total_domain_values.items()
        ]
    )
