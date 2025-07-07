## Script spec

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

