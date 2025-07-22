import gzip, json, csv
from tqdm import tqdm

DB_DIR = 'data/itdk_compiled.jsonl.gz'
OUTPUT_DIR = 'data/itdk_compiled.csv'

fields = ['IP Address', 'Node', 'ASN', 'Continent', 'Country', 'Region', 'City', 'Lat', 'Lon', 'RTT', 'VP']
with gzip.open(DB_DIR, 'rt', encoding='utf-8') as fin:
    with open(OUTPUT_DIR, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fields)
        writer.writeheader()
        for line in tqdm(fin):
            item = json.loads(line)
            writer.writerow({k: item.get(k, 'unknown') for k in fields})

