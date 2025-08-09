import gzip, argparse, json, re, pandas, os
from tqdm import tqdm
import maxminddb as mmdb
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_private(ip_addr : str) -> bool:
    ip_addr_arr = ip_addr.split('.')
    sec1, sec2 = int(ip_addr_arr[0]), int(ip_addr_arr[1])
    if (sec1 == 10 or (sec1 == 172 and (sec2 >= 16 and sec2 <= 31)) or (sec1 == 192 and sec2 == 168)):
        return True
    return False

def ipinfo_geoloc_w_asn(data, geo_reader, asn_reader):
    ret = []
    ret.append(data['src-ip'])
    ret.extend([inst['src'] for inst in data['hop-metas']])
    ret.append(data['dst-ip'])
    asn_counter = {}
    ip_addrs = [ip_addr for ip_addr in ret if not is_private(ip_addr)]

    prev_asn, prev_country = None, None
    for idx, ip_addr in enumerate(ip_addrs):
        asn, country = None, None
        asn_data = asn_reader.get(ip_addr)
        if not asn_data or not asn_data.get('autonomous_system_number', None):
            continue
        asn = f"{asn_data['autonomous_system_number']}({asn_data.get('autonomous_system_organization', 'unknown')})"
        geo_data = geo_reader.get(ip_addr)
        if not geo_data or not geo_data.get('country', None) or not geo_data['country'].get('iso_code', None):
            continue
        country = geo_data['country']['iso_code']

        if not asn or not country:
            continue
        if prev_country and country != prev_country:
            if prev_asn == 'unknown' and asn == 'unknown':
                prev_country = country
                prev_asn = asn
                continue   
            if asn == prev_asn or prev_asn == 'unknown' or asn == 'unknown':
                target = asn if prev_asn == 'unknown' else prev_asn
                asn_counter[target] = asn_counter.get(target, 0) + 1
            else:
                asn_counter[f'{prev_asn}->{asn}'] = asn_counter.get(f'{prev_asn}->{asn}', 0) + 1
        prev_country = country
        prev_asn = asn
    
    return asn_counter

def aggregate_asn_stats(item, geo_reader, asn_reader):
    if item.get('stop-reason', 'unknown') != 'completed':
        return (None, {})
    data = geo_reader.get(item['dst-ip'])
    if not data or not data.get('country', None) or not data['country'].get('iso_code', None) or data['country']['iso_code'].lower() == args.vp:
        return (None, {})
    ret = ipinfo_geoloc_w_asn(item, geo_reader, asn_reader)
    return (data['country']['iso_code'], ret)
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--vp', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--ipinfo_db', type=str, default='data/ipinfo_lite.mmdb')
    parser.add_argument('--maxmind_geodb', type=str, default='data/GeoLite2-Country.mmdb')
    parser.add_argument('--maxmind_asndb', type=str, default='data/GeoLite2-ASN.mmdb')
    parser.add_argument('--mode', type=str, default='ipinfo') 
    parser.add_argument('--worker', type=int, default=4)
    args = parser.parse_args()
    
    output_data = {}

    with mmdb.open_database(args.maxmind_geodb)as geo_reader:
        with mmdb.open_database(args.maxmind_asndb) as asn_reader:
            with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:

                def thread_fn(item):
                    return aggregate_asn_stats(item, geo_reader, asn_reader)

                for line in tqdm(f):
                    partial_dict = json.loads(line)
                    for key, value in partial_dict.items():
                        break
                    pattern = re.search(r'([\d\w\-]+)\.team\-probing\.c\d+\.\d{2}(\d{2})(\d{2})(\d{2})\.warts\.gz', key)
                    if not pattern:
                        continue
                    ident = f'{pattern.group(1)}({pattern.group(2)}-{pattern.group(3)}-{pattern.group(4)})'
                    local_dict = {}
                    with ThreadPoolExecutor(max_workers=args.worker) as executor:
                        futures = [executor.submit(thread_fn, item) for item in value]

                    for future in tqdm(as_completed(futures), total=len(futures)):
                        result = future.result()
                        if result:
                            cn, data = result
                            if cn and data:
                                local_dict.setdefault(cn, {})
                                for k, count in data.items():
                                    local_dict[cn][k] = local_dict[cn].get(k, 0) + count

                    output_data.setdefault(ident, {})
                    for cn, dist in local_dict.items():
                        output_data[ident].setdefault(cn, {})
                        for k, count in dist.items():
                            output_data[ident][cn][k] = output_data[ident][cn].get(k, 0) + count
                    
    with open(f'data/asn-meta/{args.mode}_{args.vp}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
