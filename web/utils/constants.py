
ROOT_DIR = 'images'
ASN_SUBDIR = 'crosscn-asns'
CLASSIFICATION_SUBDIR = 'classification'


DATA_ROOT_DIR = 'data'
ISO_DB = 'iso-3166-countries-with-regional-codes.csv'
SRC2DST_RAW = 'probe-filter'
SRC2DST_JSON = 'outputs'
SRC2DST_GRAPH = 'graphs'
SRC2DST_PRELIM = 'prelim'
SRC2ALL_CROSSCN = 'crosscn'
STATS_SUBFIX = {
        'Cross-country IP Link Density': '_ip_contiguous_threshold_40_crosscn_edge_heatmap.png',
        'IP Link Density': '_ip_contiguous_threshold_40_edge_heatmap.png',
        'IP Address Density': '_ip_contiguous_threshold_40_node_heatmap.png',
        'Cross-country IP Link Presence': '_ip_contiguous_presence_heatmap_crosscn_edge.png',
        'IP Link Presence': '_ip_contiguous_presence_heatmap_edge.png',
        'IP Address Presence': 'ip_contiguous_presence_heatmap_node.png',
        'Stop Hop Reasons': '_histogram.png',
        'Hop Num and RTT': 'per_date_contiguous_traceroute_preliminary_stat.png'
        }

