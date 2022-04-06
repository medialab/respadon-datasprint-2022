"""
À partir de la liste d'adresse exportée depuis la première enquête BNF sur le Covid-19
générer des listes triées des URL selon les mots-clés selon auxquelles elles sont attachées 
""" 

import csv

FILE_DATA = 'selections_covid_2020.csv'

all_keywords = set()
rows = []

with open(FILE_DATA, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')

    for row in reader:
        keywords = row['Mots clés'].split(' / ')
        for keyword in keywords:
            rows.append({
                'url': row['URL de départ'],
                'keyword': keyword
            })
            all_keywords.add(keyword)

with open('dist/url-keyword.csv', 'w', newline='') as csvfile:
    fieldnames = ['url', 'keyword']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

with open('dist/url-nb.csv', 'w', newline='') as csvfile:
    fieldnames = ['keyword', 'nb_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    nb_rows = []

    writer.writeheader()

    for keyword in list(all_keywords):
        nb_rows.append({
            'keyword': keyword,
            'nb_url': len([row for row in rows if row['keyword'] == keyword])
        })

    nb_rows = sorted(nb_rows, key=lambda d: d['nb_url'], reverse=True)
    for row in nb_rows:
        writer.writerow(row)