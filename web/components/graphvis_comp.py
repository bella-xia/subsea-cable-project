import streamlit as st
import os
from .reusable_comp import render_button
from utils.constants import ROOT_DIR, DATA_ROOT_DIR, SRC2DST_GRAPH
from utils.utils import reset_page


def render_graphvis_img(select_src, select_dst):
    if not select_src or not select_dst:
        return

    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[0]
    img_dir = f'{ROOT_DIR}/{vp}2{dst}'
    node_graph_dir, edge_graph_dir = None, None
    for f in (os.listdir(img_dir) if os.path.exists(img_dir) else []):
        if os.path.isdir(os.path.join(img_dir, f)) and f.startswith('node'):
            node_graph_dir = os.path.join(img_dir, f)
        elif os.path.isdir(os.path.join(img_dir, f)) and f.startswith('edge'):
            edge_graph_dir = os.path.join(img_dir, f)
    
    select_graph = st.segmented_control("graph specs", ("node-based", "edge-based"), selection_mode='single', on_change=reset_page)
    if select_graph:
        if (select_graph == 'node-based' and not node_graph_dir) or (select_graph == 'edge-based' and not edge_graph_dir):
            st.markdown('no data')
        else:
            images = sorted([os.path.join(node_graph_dir, img) for img in os.listdir(node_graph_dir if select_graph == 'node-based' else edge_graph_dir)])
            st.image(images[st.session_state.img_idx])
            render_button(len(images))


def render_graphvis_realtime(select_src, select_dst, processor):
    if not select_src or not select_dst or not processor:
        return

    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    img_dir = f'{DATA_ROOT_DIR}/{SRC2DST_GRAPH}/{vp}2{dst}'
    
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

        

