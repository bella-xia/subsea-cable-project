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
**dependencies**
- None

**accepted arguments**
- `--vp` [*required*] the identifier for probe data used (currently only accepts 'Kenya')
- `--dst` [*required*] the full name of the probe destination country of interest
- `--node_thres` [*default=40*] the number of row on the visual graph demonstrating per-IP utilization heatmap
- `--edge_thres` [*default=40*] the number of row on the visual graph demonstrating per IP link tuple utilization heatmap
- `--graph_thres` [*default=10*] the lower bound on the utilization count IP link tuple (per day) to be visualized on graph

**outputs**
- 'images/[*argument vp*]2[*argument dst*]' folder, including all visualizations

### vis/preliminary_visual.py
**dependencies**
- outputs of `proc/geodata_filter.py
  
**accepted arguments**
- `--input_dir` [*required*] the file path to `proc/geodata_filter.py`'s output
- `--unit` [*default=cycle*] visualize data either by probe cycle ('cycle') or by day ('date')
- `--output_dir` [*required*] the directory for image output

**outputs**
- a bar chart on probe stop reason counts
- a bar chart with the top graph on average round-trip time and the bottom graph on average hop numbers

### vis/route_presence_visual.py
**dependencies**
- output of `proc/traceroute_graph.py` with out_format set to 'json'

**accetepd arguments**
- `--input_dir` [*required*] file path to `proc/traceroute_graph.py`'s output
- `--threshold` [*default=-1*] the total number of rows in the visualization
- `--unit` [*default='ip_address'] available choice include 'ip_address' and 'asn'. Used to inform sorting algorithm used during visualization
- `--target` [*default='node'*] available choice include 'node' and 'edge'. specifies whether it is the instance or the link that is being graphed
- `--output_dir` [*required*] directory name for storing the outputted images

**outputs**
- image on most used node /edge's heatmap distribution across different days in the observed period

### proc/geodata_filter.py
**dependencies**
- MaxMind Geolocation database. Default to be stored inside `data/GeoLite2-Country.mmdb` or otherwise specified via `--geoloc_db`
- Per-country region specific metadata, used to correspond country names with continent / subregions. Default to be stored inside `data/iso-3166-countries-with-regional-codes.csv`, or otherwise specified via `--region_db`
- a jsonl.gz file parsed from raw ScamperTrace data type that contains all probes from a single vantage point, specified via `--input_dir`

**accepted arguments**
- `--input_dir` [*required*] file path to input traceroute data
- `--geoloc_db` [*default='data/GeoLite2-Country.mmdb'*] file path to MaxMind geolocation database
- `--region_db` [*default='data/iso-3166-countries-with-regional-codes.csv'*] file path to ISO database on per-country metadata (continent, subregion, intermediate region, etc.)
- `--destination` [*default=None*] the specification on which destination would the data be filtered to. If left as 'None', the script will create an overview on countries available and the number of probes per day on the country
- `--output_prefix` [*required*] used to identify each trial. If processed via pipeline, defaults to '[*vantage point*]2[*destination*]'

**outputs**
- a jsonl.gz file that contains all probe traffic data from a specified vantage point to a specified destination country 

### proc/traceroute_graph.py
**dependencies**
- MaxMind and IpInfo IP database

**accepted arguments**
- `--input_dir` [*required*] file path to `proc/geodata_filter.py`'s output
- `--threshold` [*default=None*] specifies the lower bound of the transit level on either the IP address or the IP link tuple
- `--mode` [*default='ip'`] available choice includes 'ip', 'asn', 'prefix'. Choose which one the nodes are represented to. If in asn or prefix mode consequent hops within the same ASN / Prefix will be aggregated as one hop
- `--out_format` [*default='json'*] available choice includes 'json' and 'image'. specifies whether needs outputs as json format (can be later used for `vis/route_presence_visual.py`) or as outputted image of the graphical representation per day
- `--target` [*default='node'*] available choice include 'node' and 'edge'. specifies whether the data will be filtered (by threshold) based on the transit level of the IP address or the unique IP link tuple
- `--output_prefix` [*required*] used to identify each trial. If processed via pipeline, defaults to '[*vantage point*]2[*destination*]'

**outputs**
- if `--out_format` is set to 'json', then a json file containing all the node / edge and their frequencies per day
- if `--out_format` is set to 'image', then a set of image showing the traceroute topology per day

### util/ip_checker.py
**dependencies**
- MaxMind and IpInfo IP database

**accepted arguments**
- `--query` [*default=None*] specifies what information to output. accepted input include 'who-is' (ASN info) and 'where-is'
(geolocation info). defaults None into showing both.
- `--ip` [*required*] the IP address of interest
- `--geolite_geo_db` [*default='data/GeoLite2-City.mmdb'*] file path to MaxMind Geolocation database
- `--geolite_asn_db` [*default='data/GeoLite2-ASN.mmdb'*] file path to MaxMind ASN database
- `--ipinfo_db` [*default='data/ipinfo_lite.mmdb*] file path to IpINFO database

**outputs**
- stdout aggregated info on IP address CIDR, AS-related info, geolocation-related info

