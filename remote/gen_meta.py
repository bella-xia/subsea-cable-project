import os, argparse, logging, re
from utils import sort_measure_cycle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

    
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
    parser.add_argument("-date", type=str, default=None)
    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.debug(f"address {args.directory} does not exit")
        exit(0)
    
    # get a specific path
    cycles = os.listdir(args.directory)
    sort_measure_cycle(cycles)

    print(cycles)
    
    dates_measured = os.listdir(args.directory)
    persistent_cn : set[str] = set()

    for date in dates_measured:
        path = os.path.join(args.directory, date)
        data = os.listdir(path)
    
        vp_map : dict[str, set[str]] = {}

        for d in data:
            meta = _parse_meta(d)
            if meta:
                vp_map.setdefault(meta['country-code'], set())
                vp_map[meta['country-code']].add(meta['airport'])
        
        sorted_vp_map = dict(sorted(vp_map.items(), key=lambda item: len(item[1])))
        print(sorted_vp_map['ke']) # check Kenya --> there is one airport in nbo
        if len(persistent_cn) == 0:
            persistent_cn = set(sorted_vp_map.keys())
        else:
            persistent_cn.intersection(sorted_vp_map.keys())
        
        
        # print(f"there are a total of {len(vp_map)} countries with VP")
        # print(vp_map.keys())

    # print(f"top 10 countries with the most VP: {list(sorted_vp_map.items())[-10:]}")
    # print(f"top 10 countries with the least VP: {list(sorted_vp_map.items())[:10]}")
    print(persistent_cn)