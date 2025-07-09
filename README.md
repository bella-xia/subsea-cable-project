## File structure
```plaintext
-> per_dest_pipeline.py 

-> data/ [git ignored]

-> images/ [git ignored]

-> vis/
   -> __init__.py
   -> preliminary_visual.py
   -> route_presence_visual.py
   -> crosscn_asn_visual.py

-> proc/
   -> __init__.py
   -> geodata_filter.py
   -> traceroute_graph.py
   -> aggre_crosscn_data.py
   -> explore_destinations.py
   -> traceroute_crosscn.py

-> terminal/
   -> ip_checker.py

-> remote/ [responsible for processing raw data on ssh remote server]
   -> gen_meta.py
   -> read_data.py
   -> parser.py
   -> errors.py
   -> utils.py

-> clas
   -> evaluate_distribution_shift.py
   -> evaluate_matrix_diff.py

-> utils
   -> data_processing.py

-> requirements.txt
```

## Getting Started
1. create virtual environment
2. pip install all libraries in **requirements.txt**
3. For a simple start, execute
```
python per_dest_pipeline.py --vp '[vantage point identifier]' --dst '[destination country] --prelim --node --edge --graph --crosscn_edge'
```
e.g.
```
python per_dest_pipeline.py --vp 'Kenya' --dst 'South Africa' --prelim --node --edge --graph --crosscn_edge
```
4. To obtain a selected period of time, especially if expecting the measurement duration to be contiguous (that means, a day in the middle with no measurement data suggest an actual network breakage), use
```
python per_dest_pipeline.py --vp '[vantage point identifier]' --dst '[destination country] --prelim --node --edge --graph --crosscn_edge --start [start time] --end [end-time]'
```
Both 'start' and 'end' arguments are given as *[2-digit year number]-[2-digit month number]-[2-digit day number]*, e.g.
```
python per_dest_pipeline.py --vp 'Kenya' --dst 'South Africa' --prelim --node --edge --graph --crosscn_edge --start 24-02-01 --end 24-03-30
```
## Script Spec

### per_dest_pipeline.py
**dependencies**
- None

**accepted arguments**
- `--vp` [*required*] the identifier for probe data used (currently only accepts 'Kenya')
- `--dst` [*required*] the full name of the probe destination country of interest
- `--node_thres` [*default=40*] the number of row on the visual graph demonstrating per-IP utilization heatmap
- `--edge_thres` [*default=40*] the number of row on the visual graph demonstrating per IP link tuple utilization heatmap
- `--graph_thres` [*default=10*] the lower bound on the utilization count IP link tuple (per day) to be visualized on graph
- `--start` [*default='xx'*] specification on the expected start time of the measurement. written in form '[2-digit year]-[2-digit month]-[2-digit day]'
- `--end` [*default='xx'*] specification on the expected end time of the measurement, same format as start argument
- `--prelim` [*action='store_true'*] if specified, will run script 'vis/preliminary_visual.py'. Outputs images on overall network hop number, round-trip time and stop reason statistics
- `--edge` [*action='store_true'*] if specified, will run script 'proc/traceroute_graph.py' and 'vis/route_presence_visual.py'. Outputs images on per-day heatmap of IP-link (i.e. edge of the IP-connected network graph) utilization presence and density 
- `--node` [*action='store_true'*] if specified, will run script 'proc/traceroute_graph.py' and 'vis/route_presence_visual.py'. Outputs images on per-day heatmap of IP (i.e. node of the IP-connected network graph) utilization presence and density
- `--graph` [*action='store_true'*] if specified, will run script 'proc/traceroute_graph.py'. Output per-day directed graph on IP link information obtained from per-hop IP traceroute data
- `--crosscn_edge` [*action='store_true'*] if specified, will run script 'proc/traceroute_crosscn.py' and 'vis/route_presence_visual.py'. Outputs images on per-day cross-country IP-link utilization presence and density
- `--contiguous` [*action='store_true'*] if specified, suggests that the period expects contiguous data from each day. Any day without measurement data is indicative of network disconnections

**outputs**
- 'images/[*argument vp*]2[*argument dst*]' folder, including all visualizations














