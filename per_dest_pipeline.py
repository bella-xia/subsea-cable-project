import argparse, subprocess, os, sys, re
from tqdm import tqdm

def process_script(script, args):
    command = ['python', '-m', script]
    command.extend(args)
    try:
        result = subprocess.run(
                command, check=True, text=True,
                stderr=subprocess.PIPE, stdout=sys.stdout
                )
    except subprocess.CalledProcessError as e:
        print(f'error running {script}: exited with a non-zero status code {e.returncode}')
        print(f'stderr: {e.stderr}')
        exit(-1)

    except Exception as e:
        print(f'receiving exception when running {script}: {str(e)}')
        exit(-1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--dst', type=str, default='avail')
    parser.add_argument('--vp', type=str, required=True)
    parser.add_argument('--node_thres', type=int, default=40)
    parser.add_argument('--edge_thres', type=int, default=40)
    parser.add_argument('--graph_thres', type=int, default=10)
    parser.add_argument('--vis_mode', type=str, default='both')
    parser.add_argument('--start', type=str, default='xx')
    parser.add_argument('--end', type=str, default='xx')
    parser.add_argument('--prelim', action='store_true')
    parser.add_argument('--node', action='store_true')
    parser.add_argument('--edge', action='store_true')
    parser.add_argument('--graph', action='store_true')
    parser.add_argument('--crosscn_edge', action='store_true')
    parser.add_argument('--contiguous', action='store_true')
    
    args = parser.parse_args()

    vp = re.sub(r'\s', r'', args.vp.lower())    
    if args.dst == 'avail':
        dsts = [f.split('2')[1].split('_')[0] for f in os.listdir('data/probe-filter') if f.startswith(f'{vp}2')]
    else:
        dsts = [re.sub(r'\s', r'', args.dst.lower())]
    
    for dst in tqdm(dsts):
        print(f'querying from vantage point {vp} to destination {dst}')

        prefix = f'{vp}2{dst}'  
        date_prefix = f'({args.start})2({args.end})'
        image_dir = f'images/{prefix}'
        os.makedirs(image_dir, exist_ok=True)

        # get all variables
        metadata_dir = f'data/aggre-meta/all_meta_from_{vp}.jsonl.gz'
        filtered_probe_dir = f'data/probe-filter/{prefix}_probes.jsonl.gz'
        traceroute_grah_node_dir = f'data/outputs/{date_prefix}_{prefix}_traceroutes_ip_for_node.json'
        traceroute_graph_edge_dir = f'data/outputs/{date_prefix}_{prefix}_traceroutes_ip_for_edge.json'
        traceroute_crosscn_dir = f'data/outputs/{date_prefix}_{prefix}_traceroutes_crosscn_links.json'
        
        # filter probes
        if os.path.exists(filtered_probe_dir):
            print(f'----- already filtered metadata on probes from {args.vp} to {args.dst}. skipping -----')
        else:
            print(f'----- filtering metadata on probes from {args.vp} to {args.dst} -----')
            process_script(
                    'proc.geodata_filter',
                    ['--input_dir', metadata_dir,
                     '--destination', args.dst,
                     '--output_prefix', prefix,
                     ])
        
        # preliminary visual
        if args.prelim:
            print(f'----- creating preliminary visuals on hop number and rtts -----')
            process_script(
                    'vis.preliminary_visual',
                    ['--input_dir', filtered_probe_dir,
                     '--unit', 'date',
                     '--output_dir', image_dir,
                     '--start_time', args.start,
                     '--end_time', args.end,
                     '--contiguous', str(args.contiguous)
                     ])

        # node graph   
        if args.node:
            if os.path.exists(traceroute_grah_node_dir):
                print(f'----- already created node(ip address)-based graph data. skipping -----')
            else:
                print(f'----- creating node(ip address)-based graph data -----')
                process_script(
                        'proc.traceroute_graph',
                        ['--input_dir', filtered_probe_dir,
                         '--output_prefix', prefix,
                         '--start_time', args.start,
                         '--end_time', args.end,
                         ])

            print(f'----- producing visuals on most frequently used ip address heatmap -----')
            process_script(
                    'vis.route_presence_visual',
                    ['--input_dir', traceroute_grah_node_dir,
                     '--output_dir', image_dir,
                     '--mode', args.vis_mode,
                     '--threshold', str(args.node_thres),
                     '--start_time', args.start,
                     '--end_time', args.end,
                     '--contiguous', str(args.contiguous)
                     ])

        # edge graph
        if args.edge:
            if os.path.exists(traceroute_graph_edge_dir):
                print(f'----- already created edge(path link pair)-based graph data. skipping -----')
            else:
                print(f'----- creating edge(path link pair)-based graph data -----')
                process_script(
                        'proc.traceroute_graph',
                        ['--input_dir', filtered_probe_dir,
                         '--target', 'edge',
                         '--output_prefix', prefix,
                         '--start_time', args.start,
                         '--end_time', args.end,
                         ])

            print(f'----- producing visuals on most frequently used ip tuple heatmap -----')
            process_script(
                   'vis.route_presence_visual',
                   ['--input_dir', traceroute_graph_edge_dir,
                    '--target', 'edge',
                    '--output_dir', image_dir,
                    '--mode', args.vis_mode,
                    '--threshold', str(args.edge_thres),
                    '--start_time', args.start,
                    '--end_time', args.end,
                    '--contiguous', str(args.contiguous)
                    ])

        # cross-country links
        if args.crosscn_edge:
            if os.path.exists(traceroute_crosscn_dir):
                print(f'----- already created edge(path link pair)-based cross-country graph data. skipping -----')
            else:
                print(f'----- creating edge(path link pair)-based cross-country graph data -----')
                process_script(
                        'proc.traceroute_crosscn',
                        ['--input_dir', filtered_probe_dir,
                         '--output_prefix', prefix,
                         '--start_time', args.start,
                         '--end_time', args.end,
                         ])

            print(f'----- producing visuals on most frequently used cross-country ip tuple heatmap -----')
            process_script(
                    'vis.route_presence_visual',
                    ['--input_dir', traceroute_crosscn_dir,
                     '--target', 'crosscn_edge',
                     '--output_dir', image_dir,
                     '--mode', args.vis_mode,
                     '--threshold', str(args.edge_thres),
                     '--start_time', args.start,
                     '--end_time', args.end,
                     '--contiguous', str(args.contiguous)
                     ])
       # topology graph
        if args.graph:
            print(f'----- producing graphical representations on the most utilized edges -----')
            process_script(
                    'proc.traceroute_graph',
                    ['--input_dir', filtered_probe_dir,
                     '--target', 'edge',
                     '--output_prefix', prefix,
                     '--out_format', 'image',
                     '--threshold', str(args.graph_thres)
                     ])
