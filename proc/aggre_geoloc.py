import gzip, argparse, json, re, pandas
from tqdm import tqdm
import maxminddb as mmdb
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_private(ip_addr : str) -> bool:
    # private ips include:
    # 10.0.0.0 to 10.255.255.255
    # 172.16.0.0 to 172.31.255.255
    # 192.168.0.0 to 192.168.255.255
    ip_addr_arr = ip_addr.split('.')
    sec1, sec2 = int(ip_addr_arr[0]), int(ip_addr_arr[1])
    if (sec1 == 10 or (sec1 == 172 and (sec2 >= 16 and sec2 <= 31)) or (sec1 == 192 and sec2 == 168)):
        return True
    return False

def get_city_from_ip(item: dict, country_spec: set[str], reader) -> tuple[str, dict] | None:
    ip_address = item['dst-ip']
    try:
        response = reader.get(ip_address)
        cn = response.get('country_code', None) if response else None
        if not cn or cn.lower() not in country_spec:
            return None
        cn = cn.lower()
        
        crosscn_links, crosscn_asns = set(), set()

        path = []
        path.append(item['src-ip'])
        path.extend([inst['src'] for inst in item['hop-metas']])
        path.append(item['dst-ip'])
        path = [ip_addr for ip_addr in path if not is_private(ip_addr)]
        prev_ip, prev_country, prev_asn = None, None, None

        for idx, ip_addr in enumerate(path):
            res = reader.get(ip_addr)
            if not res or not res.get('country', None):
                continue

            ip_geoloc = res['country']
            asn_name = res.get('as_name', res.get('asn', None))
            if not prev_country:
               prev_country = ip_geoloc
            elif prev_country != ip_geoloc:
                crosscn_links.add(f'{prev_ip}->{ip_addr}')
                if prev_asn:
                    crosscn_asns.add(prev_asn)
                if asn_name:
                    crosscn_asns.add(asn_name)
            prev_ip, prev_country, prev_asn = ip_addr, ip_geoloc, asn_name
     
        return (cn, item, list(crosscn_links), list(crosscn_asns))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", type=str, required=True)
    parser.add_argument('--out_prefix', type=str, required=True)
    parser.add_argument("--geoloc_db", type=str, default="data/ipinfo_lite.mmdb")
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--worker', type=int, default=4)

    args = parser.parse_args()
    
    dst_set = set(args.dst.split(','))
        
    aggre_data = {}

    with mmdb.open_database(args.geoloc_db) as reader:
        with gzip.open(args.in_path, 'rt', encoding='utf-8') as f:
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
                        cn, item, crosscn_iplink, crosscn_asn = result
                        item['crosscn-iplink'] = crosscn_iplink
                        item['crosscn-asn'] = crosscn_asn
                        spec_data[cn].append(item)
                for cn, data in spec_data.items():
                    aggre_data.setdefault(cn, {})
                    aggre_data[cn][key] = data

    for cn, per_cn_data in aggre_data.items():
        sorted_cn_data = dict(sorted(per_cn_data.items(), key=lambda item: item[0]))
        with gzip.open(args.out_prefix + f'{cn}.jsonl.gz','wt', encoding='utf-8') as f:
            for key, value in tqdm(sorted_cn_data.items()):
                json_line = json.dumps({key: value})
                f.write(json_line + '\n')
