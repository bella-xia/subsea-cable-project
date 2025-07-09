import streamlit as st
import os, re
from components.primary_select import render_primary
from components.crosscn_comp import render_crosscn_asn
from components.clasoutput_comp import render_classification
from components.prelim_comp import render_prelim
from components.heatmap_comp import render_heatmap
from components.graphvis_comp import render_graphvis
from utils.utils import define_iso, toggle_zoom
from utils.constants import DATA_ROOT_DIR, ISO_DB

if 'img_idx' not in st.session_state:
    st.session_state['img_idx'] = 0
if 'page_config' not in st.session_state:
    st.session_state['page_config'] = 'centered'
define_iso(f'{DATA_ROOT_DIR}/{ISO_DB}')

st.set_page_config(layout=st.session_state.page_config)
st.button(('zoom in' if st.session_state.page_config == 'centered' else 'zoom out'),
          on_click = toggle_zoom)
# st.title('Hello World!')
st.markdown('This serves as the visualization for subsea cable projects')


select_cat, select_src, select_dst = render_primary()

if select_cat:
    if select_cat == 'Cross-Country ASNs':
        render_crosscn_asn(select_src)
    elif select_cat == 'IP Traceroute Changes Classification Method':
        render_classification(select_src, select_dst)
    elif select_cat == 'Preliminary data':
        render_prelim(select_src, select_dst)
    elif select_cat == 'IP Utilization Heatmap':
        render_heatmap(select_src, select_dst)
    elif select_cat == 'IP Hop Connectivity Graph':
        render_graphvis(select_src, select_dst)

