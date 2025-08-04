import streamlit as st
import os, re, sys
from components.primary_select import render_primary_realtime
from components.crosscn_comp import render_crosscn_asn_realtime
from components.clasout_comp import render_clasout_realtime
from components.prelim_comp import render_prelim_realtime
from components.heatmap_comp import render_heatmap_realtime
from components.graphvis_comp import render_graphvis_realtime
from utils.utils import define_iso, toggle_zoom
from utils.constants import DATA_ROOT_DIR, ISO_DB

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from vis.preliminary_visual import prelim_image_processor
from vis.route_presence_visual import heatmap_image_processor
from vis.hop_graph_visual import graph_image_processor 
from vis.crosscn_asn_visual import crosscn_asn_processor 

if 'img_idx' not in st.session_state:
    st.session_state['img_idx'] = 0
if 'page_config' not in st.session_state:
    st.session_state['page_config'] = 'centered'
define_iso(f'{DATA_ROOT_DIR}/{ISO_DB}')

st.set_page_config(layout=st.session_state.page_config)
st.button(('zoom in' if st.session_state.page_config == 'centered' else 'zoom out'),
          on_click = toggle_zoom)
st.markdown('This serves as the visualization for subsea cable projects')

select_cat, select_src, select_dst, select_start, select_end, select_contiguous = render_primary_realtime()

if select_cat:
    if select_cat == 'Cross-Country ASNs':
        render_crosscn_asn_realtime(select_src, crosscn_asn_processor)
    elif select_cat == 'IP Traceroute Changes Classification Method':
        render_clasout_realtime(select_src, select_dst, select_start, select_end)
    elif select_cat == 'Preliminary data':
        render_prelim_realtime(select_src, select_dst, select_start, select_end, 
        select_contiguous, processor=prelim_image_processor)
    elif select_cat == 'IP Utilization Heatmap':
        render_heatmap_realtime(select_src, select_dst, select_start, select_end,    
        select_contiguous, processor=heatmap_image_processor)
    elif select_cat == 'IP Hop Connectivity Graph':
        render_graphvis_realtime(select_src, select_dst, 
        processor=graph_image_processor)
 
