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
    parser.add_argument("--destination", type=str, default=None)
    parser.add_argument('--output_prefix', type=str, required=True)

    args = parser.parse_args()
    
    continent_data = pandas.read_csv(args.region_db, on_bad_lines='skip')
    continent_data = continent_data[~continent_data['alpha-2'].isna()]
    continent_data['alpha-2'] = continent_data['alpha-2'].map(lambda x : x.lower())
    continent_data['alpha-3'] = continent_data['alpha-3'].map(lambda x : x.lower())    

    aggre_data = {}
    aggre_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {})))

    with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
        counter = 0
        for line in f:
            counter += 1
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                break

            spec_data = []
            dst_dict = defaultdict(lambda : defaultdict(int))
            print(f"querying {key}")
            for item in tqdm(value):
                data = get_city_from_ip(item['dst-ip'], args.geoloc_db)
                if data and data['country'] and data['country_code']:
                    if not args.destination:
                        # not looking for a specific destination, checking stats
                        metadata = continent_data[continent_data['alpha-2'] == data['country_code'].lower()]
                        if len(metadata) == 0:
                            continue
                        sub_region = metadata.iloc[0]['sub-region']
                        if not type(sub_region) == str:
                            continue
                        intermediate_region = metadata.iloc[0]['intermediate-region']
                        if type(intermediate_region) == str:
                            sub_region += ' - ' + intermediate_region
                        dst_dict[sub_region][data['country']] += 1
                    elif data['country'] == args.destination:
                        spec_data.append(item)

            if args.destination:
                print(f"found {len(spec_data)} instances of probes to {args.destination}")
                aggre_data[key] = spec_data
            else:
                print(f"found {len(dst_dict)} unique destination countries from the probes")
                ident = re.search(r'(c\d+\.\d+)\.', key).group(1)
                for k1, v1 in dst_dict.items():
                    for k2, v2 in v1.items():
                        aggre_dict[k1][k2][ident] = v2
                # break
            
            # if counter == 10:
            #     break
    if args.destination: 
        sorted_aggre_data = dict(sorted(aggre_data.items(), key=lambda item: item[0]))
        with gzip.open(f"data/probe_filter/{args.output_prefix}-probes.jsonl.gz",'wt', encoding='utf-8') as f:
            for key, value in sorted_aggre_data.items():
                json_line = json.dumps({key: value})
                f.write(json_line + '\n')
    else:
        with open('data/destination-probes-{args.output_prefix}.json', 'w') as f:
            json.dump(aggre_dict, f, indent=4)





