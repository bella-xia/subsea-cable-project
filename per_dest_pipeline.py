import argparse, subprocess, os, sys, re


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--vp', type=str, required=True)
    parser.add_argument('--node_thres', type=int, default=40)
    parser.add_argument('--edge_thres', type=int, default=40)
    parser.add_argument('--graph_thres', type=int, default=10)
    parser.add_argument('--start', type=str, default='xx')
    parser.add_argument('--end', type=str, default='xx')
    
    args = parser.parse_args()

    vp, dst = re.sub(r'\s', r'', args.vp.lower()), re.sub(r'\s', r'', args.dst.lower())
    PREFIX = f'{vp}2{dst}'  
    IMAGE_DIR = f'images/{PREFIX}'
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # get all variables
    METADATA_DIR = f'data/aggre-meta/all-meta-from-{vp}.jsonl.gz'
    FILTERED_PROBE_DIR = f'data/probe-filter/{PREFIX}-probes.jsonl.gz' if args.dst != 'all' else METADATA_DIR
    TRACEROUTE_GRAPH_NODE_DIR = f'data/outputs/{PREFIX}-traceroutes-ip-for-node.json'
    TRACEROUTE_GRAPH_EDGE_DIR = f'data/outputs/{PREFIX}-traceroutes-ip-for-edge.json'

    # step 1:
    if args.dst != 'all': 
        if os.path.exists(FILTERED_PROBE_DIR):
            print(f'completed step 1, filtering metadata on probes from {args.vp} to {args.dst}. skipping...')
        else:
            print(f'step 1, filtering metadata on probes from {args.vp} to {args.dst}...')
            try:
                result = subprocess.run([
                    'python', '-m', 'proc.geodata_filter',
                    '--input_dir', METADATA_DIR,
                    '--destination', args.dst,
                    '--output_prefix', PREFIX,
                    ],
                    check=True,
                    stderr=subprocess.PIPE,
                    stdout=sys.stdout,
                    text=True
                    )

            except subprocess.CalledProcessError as e:
                print(f'error running step 1: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)

            except Exception as e:
                print(f'receiving exception when running step 1: {str(e)}')
                exit(-1)
        # step 2:
    print(f'step 2, creating preliminary visuals on hop number and rtts...')
    try:
        subprocess.run([
            'python', '-m', 'vis.preliminary_visual',
            '--input_dir', FILTERED_PROBE_DIR,
            '--unit', 'date',
            '--output_dir', IMAGE_DIR
            ],
            check=True,
            stderr=subprocess.PIPE,
            stdout=sys.stdout,
            text=True
            )
    
    except subprocess.CalledProcessError as e:
        print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
        print(f'stderr: {e.stderr}')
        exit(-1)
    
    except Exception as e:
        print(f'receiving exception when running step 2: {str(e)}')
        exit(-1)
    # step 3
    if os.path.exists(TRACEROUTE_GRAPH_NODE_DIR):
        print(f'completed step 3.1, creating node(ip address)-based graph data. skipping...')
    else:
        print(f'step 3.1, creating node(ip address)-based graph data...')
        try:
            subprocess.run([
                'python', '-m', 'proc.traceroute_graph',
                '--input_dir', FILTERED_PROBE_DIR,
                '--output_prefix', PREFIX,
                '--start_time', args.start,
                '--end_time', args.end,
                ],
                check=True,
                stderr=subprocess.PIPE,
                stdout=sys.stdout,
                text=True
                )

        except subprocess.CalledProcessError as e:
            print(f'error running step 3.1: the script exited with a non-zero status code {e.returncode}')
            print(f'stderr: {e.stderr}')
            exit(-1)
 
        except Exception as e:
           print(f'receiving exception when running step 3.1: {str(e)}')
           exit(-1)

    print(f'step 3.2, producing visuals on most frequently used ip address heatmap...')
    try:
        subprocess.run([
            'python', '-m', 'vis.route_presence_visual',
            '--input_dir', TRACEROUTE_GRAPH_NODE_DIR,
            '--output_dir', IMAGE_DIR,
            '--threshold', str(args.node_thres),
            '--start_time', args.start,
            '--end_time', args.end,
            ],
            check=True,
            stderr=subprocess.PIPE,
            stdout=sys.stdout,
            text=True
            )

    except subprocess.CalledProcessError as e:
        print(f'stderr: {e.stderr}')
        exit(-1)

    except Exception as e:
        print(f'receiving exception when running step 3.2: {str(e)}')
        exit(-1)

    # step 4
    if os.path.exists(TRACEROUTE_GRAPH_EDGE_DIR):
        print(f'completed step 4.1, creating edge(path link pair)-based graph data. skipping...')
    else:
        print(f'step 4.1, create edge(path link pair)-based graph data.')
        try:
            subprocess.run([
                'python', '-m', 'proc.traceroute_graph',
                '--input_dir', FILTERED_PROBE_DIR,
                '--target', 'edge',
                '--output_prefix', PREFIX,
                '--start_time', args.start,
                '--end_time', args.end,
                ],
                check=True,
                stderr=subprocess.PIPE,
                stdout=sys.stdout,
                text=True
                )

        except subprocess.CalledProcessError as e:
            print(f'error running step 4.1: the script exited with a non-zero status code {e.returncode}')
            print(f'stderr: {e.stderr}')
            exit(-1)

        except Exception as e:
            print(f'receiving exception when running step 4.1: {str(e)}')
            exit(-1)

    print(f'step 4.2, produce visuals on most frequently used ip tuple heatmap...')
    try:
        subprocess.run([
            'python', '-m', 'vis.route_presence_visual',
            '--input_dir', TRACEROUTE_GRAPH_EDGE_DIR,
            '--target', 'edge',
            '--output_dir', IMAGE_DIR,
            '--threshold', str(args.edge_thres),
            '--start_time', args.start,
            '--end_time', args.end,           
            ],
            check=True,
            stderr=subprocess.PIPE,
            stdout=sys.stdout,
            text=True
            )

    except subprocess.CalledProcessError as e:
        print(f'error running step 4.2: the script exited with a non-zero status code {e.returncode}')
        print(f'stderr: {e.stderr}')
        exit(-1)

    except Exception as e:
        print(f'receiving exception when running step 4.2: {str(e)}')
        exit(-1)
    
    # print(f'step 5, produce graphical representations on the most utilized edges')
    # try:
    #     subprocess.run([
    #         'python', '-m', 'proc.traceroute_graph',
    #         '--input_dir', FILTERED_PROBE_DIR,
    #         '--target', 'edge',
    #         '--output_prefix', PREFIX,
    #         '--out_format', 'image',
    #         '--threshold', str(args.graph_thres)
    #         ],
    #         check=True,
    #         stderr=subprocess.PIPE,
    #         stdout=sys.stdout,
    #         text=True)

    # except subprocess.CalledProcessError as e:
    #     print(f'error running step 5: the script exited with a non-zero status code {e.returncode}')
    #     print(f'stderr: {e.stderr}')
    #     exit(-1)

    # except Exception as e:
    #     print(f'receiving exception when running step 4.2: {str(e)}')
    #     exit(-1)
    

