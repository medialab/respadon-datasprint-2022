"""
À partir de la liste d'adresse exportée depuis la première enquête BNF sur le Covid-19
Identifier des mots dans les colonnes de chaque ligne pour ranger chaque ligne dans une catégorie
"""

import pprint
import csv

FILE_DATA = 'all-url.csv'

rows = []
dictionnaire = {
    'vulgarisation': ['vulga'],
    'syndicats, association': ['ordre', 'associa', 'syndica'],
    'sites crees adhoc 2020': ['afnic', 'plateforme', 'diy'],
    'presse généraliste et locale': [
        'presse',
        'presse locale',
        'presse quotidienne',
        'theconversation.com',
        'liberation',
        'lemonde.fr',
        'lefigaro.fr',
        'leparisien',
        'lepelican',
        'www.mediapart.fr'
    ],
    'santé': [
        'infirm',
        'docteur',
        'medecin',
        'soignant',
        'professeur',
    ],
    'blog': [
        'blog',
        'blog personnel',
        'blog militant',
        'expressions individuelles',
        'journal de confinement',
        'journal personnel',
        'témoignage',
        'journal d’un médecin',
    ],
    'presse & plateformes medicales': [
        'doctissimo',
        'presse pro'
    ],
    'collectivites territoriales': [
        'mairies',
        'col. Corse',
        'munici',
        'local'
    ],
    'media influence/infox': [
       'france soir',
       'infox',
        'sputnik'
    ],
    'pharmaco, pharmaco vigileance': [],
    'etablissmeents de sante': [
        'ehpad',
        'chu'
    ]
}
url_thown = [
    'twitter.com/',
    'youtube.com/',
    'instagram.com/',
    'facebook.com/'
]

def get_category(row, heads):
    heads_to_inspect = [
        'URL de départ',
        'URL supplémentaires',
        'Mots clés',
        'Thème',
        'Notes de contenu',
        'Notes techniques',
        'Historique des URL'
    ]

    cat_extract = set()
    preuves = []

    for head in heads_to_inspect:
        row[head] = row[head].lower() if row[head] is not None else ''
        for d in dictionnaire.keys():
            filters = dictionnaire[d]
            for f in filters:
                if f in row[head]:
                    cat_extract.add(d)
                    preuve = f'{f} => ' + row[head].replace(f, f'[{f}]')
                    preuves.append(preuve)

    preuves = ' | '.join(preuves) if len(preuves) > 0 else ''

    if len(cat_extract) == 0:
        return {
            'cat': '',
            'note': False,
            'preuves': preuves
        }
    if len(cat_extract) > 1:
        msg = ' & '.join(cat_extract)
        return {
            'cat': list(cat_extract)[-1],
            'note': f'À vérifier entre {msg}',
            'preuves': preuves
        }
    else:
        return {
            'cat': list(cat_extract)[0],
            'note': False,
            'preuves': preuves
        }

def is_thrown_url(url) :
    for u in url_thown:
        if u in url:
            return True
    return False


with open(FILE_DATA, newline='') as csvfile:
    reader = csv.DictReader(csvfile, quoting=csv.QUOTE_MINIMAL)

    heads = reader.fieldnames
    heads.append('categorie')

    for row in reader:
        if row['Profondeur'] in {'websocial', 'vidéo'}:
            continue

        extraction = get_category(row, heads)

        urls = [url for url in row['URL supplémentaires'].split(' - ') if url != '']
        urls.append(row['URL de départ'])

        urls = [url for url in urls if is_thrown_url(url) == False]

        for url in urls:
            rows.append({
                'categorie': extraction['cat'],
                'note': extraction['note'] if extraction['note'] != False else '',
                'preuves': extraction['preuves'],
                'url': url,
                'mots-clés': row['Mots clés'],
                'notes de contenu': row['Notes de contenu'],
                'notes techniques': row['Notes techniques']
            })

rows = sorted(rows, key=lambda d: d['categorie'], reverse=True)

with open('dist/url-dict.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'url',
        'categorie',
        'note',
        'preuves',
        'mots-clés',
        'notes de contenu',
        'notes techniques'
    ])

    writer.writeheader()

    for row in rows:
        if row['categorie'] == '':
            continue
        writer.writerow({
            'url': row['url'],
            'categorie': row['categorie'],
            'note': row['note'],
            'preuves': row['preuves'],
            'mots-clés': row['mots-clés'],
            'notes de contenu': row['notes de contenu'],
            'notes techniques': row['notes techniques']
        })