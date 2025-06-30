import gzip, argparse, json, re, pandas, os
from tqdm import tqdm
import maxminddb as mmdb


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

def ipinfo_geoloc_w_asn(data):
    ret = []
    ret.append(data['src-ip'])
    ret.extend([inst['src'] for inst in data['hop-metas']])
    ret.append(data['dst-ip'])
    asn_counter = {}
    ip_addrs = [ip_addr for ip_addr in ret if not is_private(ip_addr)]

    prev_asn, prev_country = None, None
    for idx, ip_addr in enumerate(ip_addrs):
        asn, country = None, None
        if args.mode == 'ipinfo':
            with mmdb.open_database(args.ipinfo_db)as reader:
                data = reader.get(ip_addr)
            if not data or not data.get('country', None):
                continue
            asn = f"{data['asn']}({data.get('as_name', 'unknown')})" if data.get('asn', None) else 'unknown'
            country = data['country']
        elif args.mode == 'maxmind':
            with mmdb.open_database(args.maxmind_asndb) as reader:
                asn_data = reader.get(ip_addr)
                if not asn_data or not asn_data.get('autonomous_system_number', None):
                    continue
                asn = f"{asn_data['autonomous_system_number']}({asn_data.get('autonomous_system_organization', 'unknown')})"
            with mmdb.open_database(args.maxmind_geodb) as reader:
                geo_data = reader.get(ip_addr)
                if not geo_data or not geo_data.get('country', None):
                    continue
                country = geo_data['country']['names']['en']

        if not asn or not country:
            continue
        if prev_country and country != prev_country:
            # cross country subsea cable
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--ipinfo_db', type=str, default='data/ipinfo_lite.mmdb')
    parser.add_argument('--maxmind_geodb', type=str, default='data/GeoLite2-Country.mmdb')
    parser.add_argument('--maxmind_asndb', type=str, default='data/GeoLite2-ASN.mmdb')
    parser.add_argument('--region_db', type=str, default='data/iso-3166-countries-with-regional-codes.csv')
    parser.add_argument('--countries', type=str, required=True)
    parser.add_argument('--mode', type=str, default='maxmind') # whether to use maxmin database or ipinfo database
    args = parser.parse_args()
    
    country_set = set(args.countries.split('; '))
    iso_data = pandas.read_csv(args.region_db, on_bad_lines='skip')
    country2iso = {}
    for cn in list(country_set):
        filtered_iso = iso_data[iso_data['name'] == cn]
        if len(filtered_iso) < 1:
            country2iso[cn] = 'unknown'
        else:
            country2iso[cn] = filtered_iso.iloc[0]['alpha-2'].lower()
    
    qcns = [cn for cn, iso in country2iso.items() if (iso != 'unknown' and os.path.exists(os.path.join(args.input_dir, f'all-meta-from-{iso}.jsonl.gz')))]
    
    output_data = dict([(qcn, {}) for qcn in qcns])

    for qcn in tqdm(qcns):
        data_path = os.path.join(args.input_dir, f'all-meta-from-{country2iso[qcn]}.jsonl.gz')
        with gzip.open(data_path, 'rt', encoding='utf-8') as f:
            counter = 0
            for line in tqdm(f):
                partial_dict = json.loads(line)
                for key, value in partial_dict.items():
                    break
                pattern = re.search(r'([\d\w\-]+)\.team\-probing\.c\d+\.(\d{4})(\d{2})(\d{2})\.warts\.gz', key)
                if not pattern:
                    continue
                ident = f'{pattern.group(1)}({pattern.group(2)}-{pattern.group(3)}-{pattern.group(4)})'
                local_dict = {}
                for item in value:
                    if item.get('stop-reason', 'unknown') != 'completed':
                        continue
                    with mmdb.open_database(args.ipinfo_db)as reader:
                        data = reader.get(item['dst-ip'])
                    if not data or not data.get('country', None):
                        continue
                    cn = data['country']
                    if cn == qcn or cn not in country_set:
                        continue
                    
                    ret = ipinfo_geoloc_w_asn(item)
                    local_dict.setdefault(cn, {})
                    for k, count in ret.items():
                        local_dict.setdefault(cn, {})
                        local_dict[cn][k] = local_dict[cn].get(k, 0) + count
                

                output_data[qcn].setdefault(ident, {})
                for cn, dist in local_dict.items():
                    output_data[qcn][ident].setdefault(cn, {})
                    
                    for k, count in dist.items():
                        output_data[qcn][ident][cn][k] = output_data[qcn][ident][cn].get(k, 0) + count
                
    with open(f'data/intercontinental-data-{args.mode}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
        



