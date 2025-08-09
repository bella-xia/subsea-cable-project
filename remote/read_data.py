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
    parser.add_argument('--start_time', type=str, default='202410')
    parser.add_argument('--threshold', type=int, default=15)
    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.debug(f"address {args.directory} does not exit")
        exit(0)

    cycles = os.listdir(args.directory)
    sort_measure_cycle(cycles)
    graph_data = {}

    per_month_dict = {}
    for cycle in cycles:
        path = os.path.join(args.directory, cycle)
        if not os.path.isdir(path):
            continue
        per_month_dict.setdefault(cycle[6:12], [])
        per_month_dict[cycle[6:12]].append(cycle)

    out_dir = 'data/new-meta/aggre-' + args.country_spec
    if args.airport_spec:
        out_dir += '-' + args.airport_spec
    if args.probe_num_spec:
        out_dir += '-' + str(args.probe_num_spec)
    os.makedirs(out_dir, exist_ok=True)

    if args.airport_spec and args.probe_num_spec:
        label = rf'{args.airport_spec}{args.probe_num_spec}-{args.country_spec}\.team-probing' if args.probe_num_spec != -1 else rf'{args.airport_spec}-{args.country_spec}\.team-probing'
    elif args.airport_spec:
        label = rf'{args.airport_spec}\d*-{args.country_spec}\.team-probing'
    else:
        label = rf'{args.country_spec}\.team-probing'

    label = re.compile(label) 

    for year_mon, cycles in per_month_dict.items():
        if len(cycles) < args.threshold:
            print(f'{year_mon} only has {len(cycles)} instances. skipping')
            continue
        elif year_mon < args.start_time:
            print(f'{year_mon} is before expected start time {args.start_time}. skipping')
            continue
        print(f'available data on {year_mon}: {len(cycles)}')
        with gzip.open(os.path.join(out_dir, f'{year_mon}.jsonl.gz'), 'wt', encoding='utf-8') as f:
            for cycle in cycles:
                path = os.path.join(args.directory, cycle)

                data = [inst for inst in os.listdir(path) if label.search(inst)]
                print(f'found {len(data)} probing instance in cycle {cycle}: {data}') 
                for inst in data:
                    p = WartsDumpParser(path, inst)
                    print(f"querying capture {inst}")
                    json_line = json.dumps({inst : p.get_data('trace')})
                    f.write(json_line + '\n')
