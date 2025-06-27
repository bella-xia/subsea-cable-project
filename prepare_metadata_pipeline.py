import argparse, subprocess, os, sys, re


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--vp', type=str, required=True)
    
    args = parser.parse_args()

    vp, dst = re.sub(r'\s', r'', args.vp.lower()), re.sub(r'\s', r'', args.dst.lower())
    dsts = dst.split(',')
    print(f"preparing metadata from vantage point '{args.vp}' to destinations {dsts}")
    PREFIX = f'{vp}2{dst}'  
    os.makedirs(IMAGE_DIR, exist_ok=True)

    for dst in dsts:
        # get all variables
        METADATA_DIR = f'data/meta-aggre/all-meta-from-{vp}.jsonl.gz'
        FILTERED_PROBE_DIR = f'data/probe-filter/{PREFIX}-probes.jsonl.gz'
        TRACEROUTE_GRAPH_NODE_DIR = f'data/outputs/{PREFIX}-traceroutes-ip-for-node.json'
        TRACEROUTE_GRAPH_EDGE_DIR = f'data/outputs/{PREFIX}-traceroutes-ip-for-edge.json'
         # step 1:
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
        # step 3
        if os.path.exists(TRACEROUTE_GRAPH_NODE_DIR):
            print(f'completed step 2.1, creating node(ip address)-based graph data. skipping...')
        else:
            print(f'step 2.1, creating node(ip address)-based graph data...')
            try:
                subprocess.run([
                    'python', '-m', 'proc.traceroute_graph',
                    '--input_dir', FILTERED_PROBE_DIR,
                    '--output_prefix', PREFIX,
                    ],
                    check=True,
                    stderr=subprocess.PIPE,
                    stdout=sys.stdout,
                    text=True
                    )

            except subprocess.CalledProcessError as e:
                print(f'error running step 2.1: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)
 
            except Exception as e:
            print(f'receiving exception when running step 2.1: {str(e)}')
            exit(-1)
        # step 2.2
        if os.path.exists(TRACEROUTE_GRAPH_EDGE_DIR):
            print(f'completed step 2.2, creating edge(path link pair)-based graph data. skipping...')
        else:
            print(f'step 2.2, create edge(path link pair)-based graph data.')
            try:
                subprocess.run([
                    'python', '-m', 'proc.traceroute_graph',
                    '--input_dir', FILTERED_PROBE_DIR,
                    '--target', 'edge',
                    '--output_prefix', PREFIX,
                    ],
                    check=True,
                    stderr=subprocess.PIPE,
                    stdout=sys.stdout,
                    text=True
                    )

            except subprocess.CalledProcessError as e:
                print(f'error running step 2.2: the script exited with a non-zero status code {e.returncode}')
                print(f'stderr: {e.stderr}')
                exit(-1)

            except Exception as e:
                print(f'receiving exception when running step 2.2: {str(e)}')
            exit(-1)

