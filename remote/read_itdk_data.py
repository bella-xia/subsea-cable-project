import os, json, gzip, threading
import pandas as pd
from tqdm import tqdm

# multuthreading
from queue import Queue

# mmdb
from netaddr import IPSet
from mmdb_writer import MMDBWriter
import maxminddb

MAPPINGS = {
    'IP Address' : 'ip',
    'Node' : 'node',
    'ASN' : 'asn',
    'Continent': 'continent',
    'Country' : 'country',
    'Region' : 'region',
    'City' : 'city',
    'Lat' : 'latitude',
    'Lon' : 'longitude',
    'RTT' : 'rtt',
    'VP' : 'vp'

}
NUM_PARSERS = 4
parse_queue = Queue(maxsize=10000)
insert_queue = Queue(maxsize=10000)
writer = MMDBWriter()

def process_line(row):
    ip =row['IP Address'].strip() + '/32'
    return [ip], {v : row[k] for k, v in MAPPINGS.items() if k != 'IP Address'}

def parse_worker():
    while True:
        line = parse_queue.get()
        if line is None:
            break
        try:
            j = json.loads(line)
            insert_queue.put(process_line(j))
 
        except Exception as e:
            print(f'[Parser error] {e}')
        finally:
            parse_queue.task_done()

def write_worker():
    while True:
        item = insert_queue.get()
        if item is None:
            break
        ips, meta = item
        try:
            writer.insert_network(IPSet(ips), meta)
        except Exception as e:
            print(f'[Writer error] {e}')
        finally:
            insert_queue.task_done()

def main(input_dir):
    threads = []
    for _ in range(NUM_PARSERS):
        t = threading.Thread(target=parse_worker, daemon=True)
        t.start()
        threads.append(t)

    t_writer = threading.Thread(target=write_worker, daemon=True)
    t_writer.start()

    with gzip.open(input_dir, 'rb') as f:
        for line in f:
            parse_queue.put(line)

    for _ in threads:
        parse_queue.put(None)
    parse_queue.join()

    insert_queue.put(None)
    insert_queue.join()
    writer.to_db_file('data/itdk_formatted.mmdb')

    
if __name__ == '__main__':
    
    INPUT_DIR = 'data/itdk_compiled.jsonl.gz'
    main(INPUT_DIR)
