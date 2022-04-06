"""
À partir de la liste d'adresse exportée depuis la première enquête BNF sur le Covid-19
Identifier des mots dans les colonnes de chaque ligne pour ranger chaque ligne dans une catégorie
"""

import pprint
import csv

FILE_DATA = 'inserm.csv'

rows = []
dictionnaire = [
    'inserm',
    'pasteur',
    'chu',
    'hopita',
    'raoult',
    'ihu',
    'ministère',
    'institut',
    'académ',
    'science',
    'aphp',
    'pneumo',
    'santé.fr',
    'santé.gouv.fr',
]

with open(FILE_DATA, newline='') as csvfile:
    reader = csv.DictReader(csvfile, quoting=csv.QUOTE_MINIMAL)

    heads = reader.fieldnames
    heads.append('categorie')

    for row in reader:
        for d in dictionnaire:
            for head in heads:
                row[head] = row[head].lower() if row[head] is not None else ''
                if d in row[head]:
                    row['categorie'] = d

        rows.append(row)

rows = sorted(rows, key=lambda d: d['categorie'], reverse=True)

with open('dist/url-dict.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=heads)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)