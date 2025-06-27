import os, argparse, re, csv
from utils import sort_measure_cycle

def _parse_meta(filename: str) -> bool:
    dump_pattern = re.compile(r"(\w{3}\d*)-(\w{2})\.team-probing\.c\d{6}\.(\d{4})(\d{2})(\d{2})")
    s = dump_pattern.search(filename)
    if s:
        return {"airport" : s.group(1),
                "country-code": s.group(2),
                "year": int(s.group(3)),
                "month": int(s.group(4)),
                "day": int(s.group(5))
            }
    
    return None

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, default="/data/topology/ark/data/team-probing/list-7.allpref24/team-1/daily/2024")
    parser.add_argument("--meta_dir", type=str, default="data/iso-3166-countries-with-regional-codes.csv")
    parser.add_argument('--mode', type=str, default='vantage-point')
    parser.add_argument('--operation', type=str, default='union')
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"address {args.directory} does not exist")
        exit(0)

    if not os.path.exists(args.meta_dir):
        print(f"address {args.meta_dir} does not exist")
        exit(0)

    iso2cn_map = {}

    with open(args.meta_dir, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso2cn_map[row['alpha-2'].lower()] = row['name']
    
    # get a specific path
    cycles = os.listdir(args.directory)
    sort_measure_cycle(cycles)

    dates_measured = os.listdir(args.directory)
    persistent_cn : set[str] = set()
    persistent_vp : set[str] = set()

    for date in dates_measured:
        path = os.path.join(args.directory, date)
        data = os.listdir(path)
    
        vp_map : dict[str, set[str]] = {}

        for d in data:
            meta = _parse_meta(d)
            if meta:
                country_name = iso2cn_map.get(meta['country-code'], '')
                country_name += f'({meta["country-code"]})'
                vp_map.setdefault(country_name, set())
                vp_map[country_name].add(meta['airport'])
        
        sorted_vp_map = dict(sorted(vp_map.items(), key=lambda item: len(item[1])))
        if len(persistent_cn) == 0:
            persistent_cn = set(sorted_vp_map.keys())
        else:
            if args.operation == 'intersect':
                persistent_cn.intersection(sorted_vp_map.keys())
            elif args.operation == 'union':
                persistent_cn.union(sorted_vp_map.keys())
        
        all_vps = []
        for cn, vps in sorted_vp_map.items():
            if cn not in {'South Africa(za)', 'Tanzania, United Republic of(tz)', 'Mauritius(mu)', 'Kenya(ke)', 'Ghana(gh)', 'Israel(il)', 'Gambia(gm)', 'Madagascar(mg)'}:
                continue
            all_vps.extend([f'{cn}-{vp}' for vp in vps])
        if len(persistent_vp) == 0:
            persistent_vp = set(all_vps)
        else:
            if args.operation == 'intersect':
                persistent_vp.intersection(all_vps)
            elif args.operation == 'union':
                persistent_vp.union(all_vps)
    if args.mode == 'country':
        print(persistent_cn)
    elif args.mode == 'vantage-point':
        sorted_vp = sorted(list(persistent_vp))
        print(sorted_vp)

