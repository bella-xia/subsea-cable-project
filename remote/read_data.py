import os, argparse, logging, gzip, json, re
from parser import WartsDumpParser
from utils import sort_measure_cycle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, default="/data/topology/ark/data/team-probing/list-7.allpref24/team-1/daily/2024")
    parser.add_argument('--country_spec', type=str, required=True)
    parser.add_argument('--airport_spec', type=str, default=None)
    parser.add_argument('--probe_num_spec', type=int, default=None)
    args = parser.parse_args()

    if args.airport_spec and args.probe_num_spec:
        label = rf'{args.airport_spec}{args.probe_num_spec}-{args.country_spec}\.team-probing' if args.probe_num_spec != -1 else rf'{args.airport_spec}-{args.country_spec}\.team-probing'
    elif args.airport_spec:
        label = rf'{args.airport_spec}\d*-{args.country_spec}\.team-probing'
    else:
        label = rf'{args.country_spec}\.team-probing'

    if not os.path.exists(args.directory):
        logger.debug(f"address {args.directory} does not exit")
        exit(0)

    label = re.compile(label) 
    # get a specific path
    cycles = os.listdir(args.directory)
    sort_measure_cycle(cycles)
    graph_data = {}

    for cycle in cycles:
        path = os.path.join(args.directory, cycle)
        if not os.path.isdir(path):
            continue
        data = [inst for inst in os.listdir(path) if label.search(inst)]
        print(f'found {len(data)} probing instance in cycle {cycle}: {data}') 
        for inst in data:
            p = WartsDumpParser(path, inst)
            print(f"querying capture {inst}")
            graph_data[inst] = p.get_data('trace')
   
    output_dir = 'data/all_meta_from_' + args.country_spec
    if args.airport_spec:
        output_dir += '_' + args.airport_spec
    if args.probe_num_spec:
        output_dir += '_' + str(args.probe_num_spec)
    output_dir += '.jsonl.gz'
    with gzip.open(output_dir, 'wt', encoding='utf-8') as f:
        for key, value in graph_data.items():
            json_line = json.dumps({key: value})
            f.write(json_line + '\n')
    
