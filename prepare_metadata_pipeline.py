import argparse, subprocess, os, sys, re
import pandas as pd

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, default='data/meta')
    parser.add_argument('--iso_db', type=str, default='data/iso-3166-countries-with-regional-codes.csv')
    args = parser.parse_args()
    
    # process iso data
    iso_data = pd.read_csv(args.iso_db)
    iso_data = iso_data[~iso_data['alpha-2'].isna()]
    iso_data = iso_data[['name', 'alpha-2']]
    iso2cn = {iso_data.iloc[i]['alpha-2'].lower(): iso_data.iloc[i]['name'] for i in range(len(iso_data))}
    iso2cn['uk'] = 'United Kingdom'
    cn2iso = {v : k for k, v in iso2cn.items()}

    meta_files = os.listdir(args.root_dir)
    avail_iso = [inst.split('.')[0].split('_')[-1] for inst in meta_files]
    avail_cns = [iso2cn[iso] for iso in avail_iso if iso2cn.get(iso, None)]
    assert(len(avail_iso) == len(avail_cns))
    print(f'gathering data for available countries: {avail_cns}')

    os.makedirs('data/probe-filter', exist_ok=True)
    os.makedirs('data/outputs', exist_ok=True)
    os.makedirs('data/graphs', exist_ok=True)
    os.makedirs('data/crosscn', exist_ok=True)
    os.makedirs('data/asn-meta', exist_ok=True)
    os.makedirs('data/prelim', exist_ok=True)

    for vp_idx in range(len(avail_iso)):
        vp = avail_iso[vp_idx]
        avail_dst = [dst for dst in avail_iso if dst != vp]
        META_GEODATA_DIR = f'{args.root_dir}/all_meta_from_{vp}.jsonl.gz'
        META_ASNDATA_DIR = f'data/asn-meta/maxmind_{vp}.json'
        CROSSCN_ASN_DIR = f'data/crosscn/maxmind_{vp}.json'

        # step 1: aggregate geoloc data
        q_dst = [dst for dst in avail_dst if not os.path.exists(f'data/probe-filter/{vp}2{dst}_probes.jsonl.gz')]
        if len(q_dst) == 0:
            print(f'completed step 1, aggregating geoloc metadata on probes from {vp} to {q_dst}. skipping...')
        else:
            print(f'step 1: aggregating geoloc metadata on probes from {vp} to {q_dst}')
            try:
                result = subprocess.run([
                    'python', '-m', 'proc.aggre_geoloc',
                    '--input_dir', META_GEODATA_DIR, 
                    '--vp', vp, 
                    '--dst', ','.join(q_dst),
                    ],
                    check=True, 
                    text=True, 
                    stderr=subprocess.PIPE, 
                    stdout=sys.stdout
                )

            except subprocess.CalledProcessError as e:
                print(f'error running step 1: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)

            except Exception as e:
                print(f'receiving exception when running step 1: {str(e)}')
                exit(-1)

        # step 2: aggregate asn data
        if os.path.exists(META_ASNDATA_DIR):
            print(f'completed step 2, aggregating asn metadata on probes from {vp} to {avail_dst}. skipping...')
        else:
            print(f'step 2: aggregating asn metadata on probes from {vp} to {avail_dst}')
            try:
                result = subprocess.run([
                    'python', '-m', 'proc.aggre_asn',
                    '--input_dir', META_GEODATA_DIR, 
                    '--vp', vp, 
                    '--dst', ','.join(avail_dst),
                    ],
                    check=True, 
                    text=True, 
                    stderr=subprocess.PIPE, 
                    stdout=sys.stdout
                )

            except subprocess.CalledProcessError as e:
                print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)

            except Exception as e:
                print(f'receiving exception when running step 2: {str(e)}')
                exit(-1)

        # step 3: generate asn distribution data for specified dst cns
        if os.path.exists(CROSSCN_ASN_DIR):
            print(f'completed step 3, generating asn distribution data from {vp} to {avail_dst}. skipping...')
        else:
            print(f'step 3: generating asn distribution data from {vp} to {avail_dst}')
            try:
                result = subprocess.run([
                    'python', '-m', 'proc.gen_asndist',
                    '--input_dir', META_ASNDATA_DIR, 
                    '--dst', ','.join(avail_dst),
                    '--prefix', f"{vp}2{'+'.join(avail_dst)}"
                    ],
                    check=True, 
                    text=True, 
                    stderr=subprocess.PIPE, 
                    stdout=sys.stdout
                )

            except subprocess.CalledProcessError as e:
                print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)

            except Exception as e:
                print(f'receiving exception when running step 2: {str(e)}')
                exit(-1)
        for dst in avail_dst:
            PREFIX = f'{vp}2{dst}'
            FILTERED_PROBE_DIR = f'data/probe-filter/{PREFIX}_probes.jsonl.gz'
            PRELIM_DATA_DIR = f'data/prelim/{PREFIX}.json'
            TRACEROUTE_GRAPH_NODE_DIR = f'data/outputs/{PREFIX}_node.json'
            TRACEROUTE_GRAPH_EDGE_DIR = f'data/outputs/{PREFIX}_edge.json'
            TRACEROUTE_CROSSCN_DIR = f'data/outputs/{PREFIX}_crosscn_edge.json'
            TRACEROUTE_GRAPHVIS_DIR = f'data/graphs/{PREFIX}'
            
            # step 4: generate preliminary data
            if os.path.exists(PRELIM_DATA_DIR):
                print(f'completed step 4, generate preliminary data from {vp} to {dst}. skipping...')
            else:
                print(f'step 4: generating preliminary data from {vp} to {dst}')
                try:
                   subprocess.run([
                       'python', '-m', 'proc.gen_prelim',
                       '--input_dir', FILTERED_PROBE_DIR,
                       '--output_prefix', PREFIX
                       ],
                       check=True, 
                       text=True, 
                       stderr=subprocess.PIPE, 
                       stdout=sys.stdout
                   )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 4: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)
     
                except Exception as e:
                    print(f'receiving exception when running step 4: {str(e)}')
                    exit(-1)
                   
            # step 5: generate traceroute graph json on IP and IP link
            if os.path.exists(TRACEROUTE_GRAPH_NODE_DIR):
                print(f'completed step 4.1, generating node(ip address)-based graph data from {vp} to {dst}. skipping...')
            else:
                print(f'step 4.1: generating node(ip address)-based graph data from {vp} to {dst}.')
                try:
                    subprocess.run([
                        'python', '-m', 'proc.gen_tracegraph',
                        '--input_dir', FILTERED_PROBE_DIR,
                        '--output_prefix', PREFIX
                        ],
                        check=True, 
                        text=True, 
                        stderr=subprocess.PIPE, 
                        stdout=sys.stdout
                    )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 4.1: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)
     
                except Exception as e:
                    print(f'receiving exception when running step 4.1: {str(e)}')
                    exit(-1)

            if os.path.exists(TRACEROUTE_GRAPH_EDGE_DIR):
                print(f'completed step 4.2, creating edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
            else:
                print(f'step 4.2, create edge(path link pair)-based graph data from {vp} to {dst}.')
                try:
                    subprocess.run([
                        'python', '-m', 'proc.gen_tracegraph',
                        '--input_dir', FILTERED_PROBE_DIR,
                        '--output_prefix', PREFIX,
                        '--target', 'edge',
                        ],
                        check=True,
                        text=True,
                        stderr=subprocess.PIPE,
                        stdout=sys.stdout,
                        )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 4.2: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)

                except Exception as e:
                    print(f'receiving exception when running step 4.2: {str(e)}')
                    exit(-1)
            
            # step 5: generate traceroute graph on IP and IP link
            if os.path.exists(TRACEROUTE_GRAPHVIS_DIR):
                print(f'completed step 5, generating graph visual data from {vp} to {dst}. skipping...')
            else:
                print(f'step 5: generating graph visual data from {vp} to {dst}.')
                try:
                    subprocess.run([
                        'python', '-m', 'proc.gen_tracegraph',
                        '--input_dir', FILTERED_PROBE_DIR,
                        '--output_prefix', PREFIX,
                        '--out_format', 'xml'
                        ],
                        check=True, 
                        text=True, 
                        stderr=subprocess.PIPE, 
                        stdout=sys.stdout
                    )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 5: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)
     
                except Exception as e:
                    print(f'receiving exception when running step 4: {str(e)}')
                    exit(-1)

            # step 6: generate traceroute graph on cross-cn link

            if os.path.exists(TRACEROUTE_CROSSCN_DIR):
                print(f'completed step 6, generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
            else:
                print(f'step 6: generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}.')
                try:
                    subprocess.run([
                        'python', '-m', 'proc.gen_crosscn',
                        '--input_dir', FILTERED_PROBE_DIR,
                        '--output_prefix', PREFIX,
                        ],
                        check=True,
                        text=True,
                        stderr=subprocess.PIPE,
                        stdout=sys.stdout
                        )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 6: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)

                except Exception as e:
                    print(f'receiving exception when running step 6: {str(e)}')
                    exit(-1)
 
