## Script spec

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
