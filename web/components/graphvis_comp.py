import streamlit as st
import os
from .reusable_comp import render_button
from utils.constants import STATS_ROOT_DIR, SRC2DST_GRAPH
from utils.utils import reset_page

def render_graphvis_realtime(select_src, select_dst, processor):
    if not select_src or not select_dst or not processor:
        return

    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    img_dir = f'{STATS_ROOT_DIR}/{SRC2DST_GRAPH}/{vp}2{dst}'
    
    if not os.path.exists(img_dir):
        st.write(f'no graph data available for {vp}2{dst} at {img_dir}')
    else:
        graphs = os.listdir(img_dir)
        graphs = sorted(graphs)
        select_graph = st.segmented_control("graph specs", ("node", "edge"), default='node', selection_mode='single')
        select_threshold = st.slider('threshold', min_value=0, max_value=100, value=0)
        fig = processor(os.path.join(img_dir, graphs[st.session_state.img_idx]), select_graph, select_threshold)
        st.caption(graphs[st.session_state.img_idx].split('_')[0])
        st.pyplot(fig)
        render_button(len(graphs))

        

