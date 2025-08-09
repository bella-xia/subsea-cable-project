import argparse, subprocess, os, sys, re
import pandas as pd

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, default='data')
    parser.add_argument('--data_dir', type=str, default='north-europe-meta')
    parser.add_argument('--iso_db', type=str, default='data/iso-3166-countries-with-regional-codes.csv')
    args = parser.parse_args()
    
    # process iso data
    iso_data = pd.read_csv(args.iso_db)
    iso_data = iso_data[~iso_data['alpha-2'].isna()]
    iso_data = iso_data[['name', 'alpha-2']]
    iso2cn = {iso_data.iloc[i]['alpha-2'].lower(): iso_data.iloc[i]['name'] for i in range(len(iso_data))}
    cn2iso = {v : k for k, v in iso2cn.items()}

    meta_files = os.listdir(f'{args.root_dir}/{args.data_dir}')
    avail_iso = [inst.split('.')[0].split('-')[-1] for inst in meta_files]
    avail_cns = [iso2cn[iso] for iso in avail_iso if iso2cn.get(iso, None)]
    assert(len(avail_iso) == len(avail_cns))
    print(f'gathering data for available countries: {avail_cns}')

    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(f'{args.data_dir}/probe-filter', exist_ok=True)
    os.makedirs(f'{args.data_dir}/outputs', exist_ok=True)
    os.makedirs(f'{args.data_dir}/graphs', exist_ok=True)
    os.makedirs(f'{args.data_dir}/crosscn', exist_ok=True)
    os.makedirs(f'{args.data_dir}/asn-meta', exist_ok=True)
    os.makedirs(f'{args.data_dir}/prelim', exist_ok=True)

    for vp_idx in range(len(avail_iso)):
        vp = avail_iso[vp_idx]
        avail_dst = [dst for dst in avail_iso if dst != vp]

        meta_geodata_dir = f'{args.root_dir}/{args.data_dir}/aggre-{vp}'
        probe_filter_dir = f'{args.data_dir}/probe-filter'

        for month_file in os.listdir(meta_geodata_dir):
            meta_geodata_path = f'{meta_geodata_dir}/{month_file}'
            month_spec = month_file.split('.')[0]

            # step 1: aggregate geoloc data
            q_dst = [dst for dst in avail_dst if not os.path.exists(f'{probe_filter_dir}/{month_spec}_{vp}2{dst}.jsonl.gz')]
            if len(q_dst) == 0:
                print(f'completed step 1, aggregating geoloc metadata on probes from {vp} to {q_dst}. skipping...')
            else:
                print(f'step 1: aggregating geoloc metadata on probes from {vp} to {q_dst}')
                try:
                    result = subprocess.run([
                        'python', '-m', 'proc.aggre_geoloc',
                        '--in_path', meta_geodata_path,
                        '--out_prefix', f'{probe_filter_dir}/{month_spec}_{vp}2',
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

            # # step 3: generate asn distribution data for specified dst cns
            # if os.path.exists(crosscn_asn_dir):
            #     print(f'completed step 3, generating asn distribution data from {vp} to {avail_dst}. skipping...')
            # else:
            #     print(f'step 3: generating asn distribution data from {vp} to {avail_dst}')
            #     try:
            #         result = subprocess.run([
            #             'python', '-m', 'proc.gen_asndist',
            #             '--input_dir', META_ASNDATA_DIR, 
            #             '--dst', ','.join(avail_dst),
            #             '--prefix', f"{vp}2{'+'.join(avail_dst)}"
            #             ],
            #             check=True, 
            #             text=True, 
            #             stderr=subprocess.PIPE, 
            #             stdout=sys.stdout
            #         )

            #     except subprocess.CalledProcessError as e:
            #         print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
            #         print(f'stderr: {e.stderr}')
            #         exit(-1)

            #     except Exception as e:
            #         print(f'receiving exception when running step 2: {str(e)}')
            #         exit(-1)

            for dst in avail_dst:
                prefix = f'{vp}2{dst}'
                probe_filter_path = f'{probe_filter_dir}/{month_spec}_{prefix}.jsonl.gz'
                prelim_dir = f'{args.data_dir}/prelim'
                prelim_path = f'{prelim_dir}/{month_spec}_{prefix}.json'

                graph_json_dir = f'{args.data_dir}/outputs'
                graph_node_path = f'{graph_json_dir}/{month_spec}_{prefix}_node.json'
                graph_edge_path = f'{graph_json_dir}/{month_spec}_{prefix}_edge.json'
                graph_crosscn_path = f'{graph_json_dir}/{month_spec}_{prefix}_crosscn_edge.json'
                graph_vis_dir = f'{args.data_dir}/graphs/{month_spec}_{prefix}'
                
                # step 4: generate preliminary data
                if os.path.exists(prelim_path):
                    print(f'completed step 4, generate preliminary data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 4: generating preliminary data from {vp} to {dst}')
                    try:
                       subprocess.run([
                           'python', '-m', 'proc.gen_prelim',
                           '--in_path', probe_filter_path,
                           '--out_path', prelim_path
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
                if os.path.exists(graph_node_path):
                    print(f'completed step 4.1, generating node(ip address)-based graph data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 4.1: generating node(ip address)-based graph data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_node_path
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

                if os.path.exists(graph_edge_path):
                    print(f'completed step 4.2, creating edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 4.2, create edge(path link pair)-based graph data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_edge_path,
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
                if os.path.exists(graph_vis_dir):
                    print(f'completed step 5, generating graph visual data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 5: generating graph visual data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_vis_dir,
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
                # if os.path.exists(graph_crosscn_path):
                #     print(f'completed step 6, generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
                # else:
                #     print(f'step 6: generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}.')
                #     try:
                #         subprocess.run([
                #             'python', '-m', 'proc.gen_crosscn',
                #             '--input_dir', FILTERED_PROBE_DIR,
                #             '--output_prefix', PREFIX,
                #             ],
                #             check=True,
                #             text=True,
                #             stderr=subprocess.PIPE,
                #             stdout=sys.stdout
                #             )

                #     except subprocess.CalledProcessError as e:
                #         print(f'error running step 6: the script exited with a non-zero status code {e.returncode}')
                #         print(f'stderr: {e.stderr}')
                #         exit(-1)

                #     except Exception as e:
                #         print(f'receiving exception when running step 6: {str(e)}')
                #         exit(-1)
     
