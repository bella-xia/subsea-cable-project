import argparse, json


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/destination-probes-from-kenya.json')

    args = parser.parse_args()


    with open(args.input_dir, 'r') as f:
        data = json.load(f)
    

    target_probes = ['Northern Europe',
                     'Western Europe',
                     'Sub-Saharan Africa - Southern Africa',
                     'Sub-Saharan Africa - Eastern Africa',
                     'Sub-Saharan Africa - Western Africa',
                     'Western Asia']

    for probe in target_probes:
        subregion_data = data[probe]
        country_probe_pair = [(k1, sum([v2 for _, v2 in v1.items()])) for k1, v1 in subregion_data.items()]
        sorted_pair = sorted(country_probe_pair, key=lambda x : x[1], reverse=True)
        print(f"{probe}: {sorted_pair[:3]}")

