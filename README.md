## File structure
```plaintext
-> per_dest_pipeline.py 

-> data/ [git ignored]

-> images/ [git ignored]

-> vis/
   -> __init__.py
   -> preliminary_visual.py
   -> route_presence_visual.py

-> proc/
   -> __init__.py
   -> geodata_filter.py
   -> traceroute_graph.py

-> util/
   -> ip_checker.py

-> requirements.txt
```

## Getting Started
1. create virtual environment
2. pip install all libraries in **requirements.txt**
3. For a simple start, execute
```
python per_dest_pipeline.py --vp '[vantage point identifier]' --dst '[destination country]'
```
e.g.
```
python per_dest_pipeline.py --vp 'Kenya' --dst 'South Africa'
```

## Script Spec

### per_dest_pipeline.py
dependencies:
- None

accepted arguments:
- `--vp` [*required*] the identifier for probe data used (currently only accepts 'Kenya')
- `--dst` [*required*] the full name of the probe destination country of interest
- `--node_thres` [*default=40*] the number of row on the visual graph demonstrating per-IP utilization heatmap
- `--edge_thres` [*default=40*] the number of row on the visual graph demonstrating per IP link tuple utilization heatmap
- `--graph_thres` [*default=10*] the lower bound on the utilization count IP link tuple (per day) to be visualized on graph

outputs:
- **"images/[*argument vp*]2[*argument dst*]"** folder, including all visualizations

### vis/preliminary_visual.py
dependencies:
- outputs of `proc/geodata_filter.py`
  
accepted arguments:

outputs:

### vis/route_presence_visual.py

### proc/geodata_filter.py
dependencies:
- MaxMind Geolocation database. Default to be stored inside `data/GeoLite2-Country.mmdb` or otherwise specified via `--geoloc_db`
- Per-country region specific metadata, used to correspond country names with continent / subregions. Default to be stored inside `data/iso-3166-countries-with-regional-codes.csv`, or otherwise specified via `--region_db`
- a jsonl.gz file parsed from raw ScamperTrace data type that contains all probes from a single vantage point, specified via `--input_dir`

accepted arguments:
- `--input_dir` [*required*] file path to input traceroute data
- `--geoloc_db` [*default='data/iso-3166-countries-with-regional-codes.csv'*] file path to MaxMind geolocation database
- `--region_db` [*default='data/iso

outputs:
- a jsonl.gz file that contains all probe traffic data from a specified vantage point to a specified destination country 

### proc/traceroute_graph.py

### util/ip_checker.py

