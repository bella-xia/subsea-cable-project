import gzip, argparse, json, re, pandas
from tqdm import tqdm
import geoip2.database
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_city_from_ip(item: dict, country_spec: set[str], reader) -> tuple[str, dict] | None:
    ip_address = item['dst-ip']
    try:
        city_data = None
        response = reader.country(ip_address)
        cn = response.country.iso_code.lower() if (response and response.country and response.country.iso_code) else None
        if not cn or cn not in country_spec:
            return None
        return (cn, item)
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--geoloc_db", type=str, default="data/GeoLite2-Country.mmdb")
    parser.add_argument('--vp', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--worker', type=int, default=4)

    args = parser.parse_args()
    
    dst_set = set(args.dst.split(','))
        
    aggre_data = {}
    counter = 0

    with geoip2.database.Reader(args.geoloc_db) as reader:
        with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
            def thread_fn(item):
                return get_city_from_ip(item, dst_set, reader)

            for line in f:
                partial_dict = json.loads(line)
                for key, value in partial_dict.items():
                    break
                spec_data = defaultdict(list)
                with ThreadPoolExecutor(max_workers=args.worker) as executor:
                    futures = [executor.submit(thread_fn, item) for item in value]

                for future in tqdm(as_completed(futures), total=len(futures)):
                    result = future.result()
                    if result:
                        cn, item = result
                        spec_data[cn].append(item)
            
                for cn, data in spec_data.items():
                    aggre_data.setdefault(cn, {})
                    aggre_data[cn][key] = data

    for cn, per_cn_data in aggre_data.items():
        sorted_cn_data = dict(sorted(per_cn_data.items(), key=lambda item: item[0]))
        with gzip.open(f"data/probe-filter/{args.vp}2{cn}_probes.jsonl.gz",'wt', encoding='utf-8') as f:
            for key, value in tqdm(sorted_cn_data.items()):
                json_line = json.dumps({key: value})
                f.write(json_line + '\n')
