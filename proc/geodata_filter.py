import gzip, argparse, json, re, pandas
from tqdm import tqdm
import geoip2.database
from collections import defaultdict

def get_city_from_ip(ip_address, database_path):
    try:
        with geoip2.database.Reader(database_path) as reader:
            response = reader.country(ip_address)
            city_data = {
                "country": response.country.name,
                "country_code": response.country.iso_code
            }
        return city_data
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--geoloc_db", type=str, default="data/GeoLite2-Country.mmdb")
    parser.add_argument("--region_db", type=str, default="data/iso-3166-countries-with-regional-codes.csv")
    parser.add_argument('--vp', type=str, required=True)
    parser.add_argument('--dst', type=str, default=None)

    args = parser.parse_args()

    if not args.dst or not len(args.dst):
        print(f'invalid destination specification')
        exit(0)
    
    dst_set = set(args.dst.split(', '))
    print(dst_set)
    continent_data = pandas.read_csv(args.region_db, on_bad_lines='skip')
    continent_data = continent_data[~continent_data['alpha-2'].isna()]
    continent_data['alpha-2'] = continent_data['alpha-2'].map(lambda x : x.lower())
    continent_data['alpha-3'] = continent_data['alpha-3'].map(lambda x : x.lower())    
    
    aggre_data = {}
    counter = 0
    with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
        for line in f:
            counter += 1
            partial_dict = json.loads(line)
            # each key here is a probe file name, specified as
            # .... c011243.20240130.....
            for key, value in partial_dict.items():
                break
            print(f"querying probe file '{key}'")
            spec_data = defaultdict(list)
            for item in tqdm(value):
                data = get_city_from_ip(item['dst-ip'], args.geoloc_db)
                if not data or not data['country']:
                    continue

                if data['country'] in dst_set:
                    spec_data[data['country']].append(item)
            
            for cn, data in spec_data.items():
                aggre_data.setdefault(cn, {})
                aggre_data[cn][key] = data
        
    for cn, per_cn_data in aggre_data.items():
        sorted_cn_data = dict(sorted(per_cn_data.items(), key=lambda item: item[0]))
        cn = re.sub(r'\s', r'', cn.lower())
        with gzip.open(f"data/probe-filter/{args.vp}2{cn}-probes.jsonl.gz",'wt', encoding='utf-8') as f:
            for key, value in tqdm(sorted_cn_data.items()):
                json_line = json.dumps({key: value})
                f.write(json_line + '\n')




