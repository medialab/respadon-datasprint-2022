import sys
import csv
from collections import defaultdict

INDEX = defaultdict(list)

with open(sys.argv[1], encoding='utf8') as f:
    reader = csv.DictReader(f, delimiter=';')

    for row in reader:
        if row['Date'] != '2021':
            continue

        INDEX[row["URL de départ"]].append(row)

UNIQUE_URLS = set()

for url, rows in INDEX.items():
    for row in rows:
        UNIQUE_URLS.add(row["URL de départ"])

writer = csv.writer(sys.stdout)
writer.writerow(['seed_url'])

for url in sorted(UNIQUE_URLS):
    writer.writerow([url])
