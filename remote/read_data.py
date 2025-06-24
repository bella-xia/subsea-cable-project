import os, argparse, logging, gzip, json
from parser import WartsDumpParser
from utils import sort_measure_cycle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, default="/data/topology/ark/data/team-probing/list-7.allpref24/team-1/daily/2024")
    parser.add_argument("-date", type=str, default=None)
    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.debug(f"address {args.directory} does not exit")
        exit(0)
    
    # get a specific path
    cycles = os.listdir(args.directory)
    sort_measure_cycle(cycles)

    graph_data = {}

    for cycle in cycles:
        path = os.path.join(args.directory, cycle)
        data = [inst for inst in os.listdir(path) if inst.startswith('nbo-ke.team-probing')]
        
        for inst in data:
            p = WartsDumpParser(path, inst)
            print(f"querying capture {inst}")
            # p.demo_data('trace', num_vis=1)
            graph_data[inst] = p.get_data('trace')

    with gzip.open('data/all-meta-from-kenya-w-status.jsonl.gz', 'wt', encoding='utf-8') as f:
        for key, value in graph_data.items():
            json_line = json.dumps({key: value})
            f.write(json_line + '\n')
    
