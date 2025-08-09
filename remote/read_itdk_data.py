import os, json, gzip, threading, time
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
line_counter, parse_counter, write_counter = 0, 0, 0
counter_lock = threading.Lock()

def process_line(row):
    ip =row['IP Address'].strip() + '/32'
    return [ip], {v : row[k] for k, v in MAPPINGS.items() if k != 'IP Address' and row[k] is not None}

def parse_worker():
    global parse_counter
    while True:
        line = parse_queue.get()
        if line is None:
            print('[INFO] parse worker exiting...')
            parse_queue.task_done()
            break
        try:
            j = json.loads(line)
            insert_queue.put(process_line(j))
 
        except Exception as e:
            print(f'[PARSER ERROR] {e}')
        finally:
            with counter_lock:
                parse_counter += 1
            parse_queue.task_done()

def monitor_worker():
    global parse_counter, write_counter, line_counter
    while True:
        time.sleep(1800) # log every half an hour
        with counter_lock:
            pct = (parse_counter / line_counter) * 100 if line_counter else 0
            print(f'[MONITOR] Processed {parse_counter}/{line_counter} lines ({pct:.2f}%)')
            wct = (write_counter / parse_counter) * 100 if parse_counter else 0
            print(f'[MONITOR] Written {write_counter} / {parse_counter} lines ({wct:.2f}%)')

def write_worker():
    global write_counter
    while True:
        item = insert_queue.get()
        if item is None:
            print('[INFO] write worker exiting...')
            insert_queue.task_done()
            break
        ips, meta = item
        try:
            writer.insert_network(IPSet(ips), meta)
        except Exception as e:
            print(f'[WRITER ERROR] {e}')
        finally:
            with counter_lock:
                write_counter += 1
            insert_queue.task_done()

def main(input_dir):
    global line_counter
    threads = []

    for _ in range(NUM_PARSERS):
        t = threading.Thread(target=parse_worker, daemon=False)
        t.start()
        threads.append(t)

    t_writer = threading.Thread(target=write_worker, daemon=False)
    t_writer.start()

    t_monitor = threading.Thread(target=monitor_worker, daemon=True)
    t_monitor.start()
    
    with gzip.open(input_dir, 'rb') as f:
        for line in f:
            parse_queue.put(line)
            with counter_lock:
                line_counter += 1

    for _ in threads:
        parse_queue.put(None)
    for _ in threads:
        t.join()
    
    print('[INFO] joined all parse thread')
    parse_queue.join()
    print('[INFO] joined parse queue')
    insert_queue.put(None)
    t_writer.join()
    print('[INFO] joined writer')
    insert_queue.join()
    writer.to_db_file('data/itdk_formatted.mmdb')
    
if __name__ == '__main__':
    
    INPUT_DIR = 'data/itdk_compiled.jsonl.gz'
    main(INPUT_DIR)
