import csv
import multiprocessing as mp

INPUT_FILE = 'data/itdk_compiled.csv'
OUTPUT_FILE = 'data/itdk_formalized.csv'
NUM_WORKERS = 4

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

def process_line(row):
    row['IP Address'] =row['IP Address'].strip() + '/32'
    return {v : row[k] for k, v in MAPPINGS.items()}

def worker(row_queue, result_queue):
    while True:
        row = row_queue.get()
        if not row:
            break
        result = process_line(row)
        result_queue.put(result)


def writer(result_queue, done_event):
    with open(OUTPUT_FILE, 'w', newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=MAPPINGS.values())
        writer.writeheader()
        while not done_event.is_set() or not result_queue.empty():
            try:
                row = result_queue.get(timeout=0.1)
                writer.writerow(row)
            except:
                continue

def main():
    row_queue = mp.Queue(maxsize=1000)
    result_queue = mp.Queue(maxsize=1000)
    done_event = mp.Event()

    writer_process = mp.Process(target=writer, 
                        args=(result_queue, done_event))
    writer_process.start()

    workers = [mp.Process(target=worker, 
                args=(row_queue, result_queue)) for _ in range(NUM_WORKERS)]
    for w in workers:
        w.start()

    with open(INPUT_FILE, 'r') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            row_queue.put(row)
    print('completes feeding reader data into queue') 
    for _ in workers:
        row_queue.put(None)

    for w in workers:
        w.join()

    done_event.set()
    writer_process.join()

if __name__ == '__main__':
    main()
