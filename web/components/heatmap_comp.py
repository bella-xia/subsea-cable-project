import streamlit as st
from utils.utils import extract_stats_images
from utils.constants import STATS_ROOT_DIR, SRC2DST_JSON
import os, datetime
from .reusable_comp import savefig_button

def render_heatmap_realtime(select_src, select_dst, select_start, select_end, select_contiguous, processor=None):
    if not select_src or not select_dst or not processor or not select_start or not select_end:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    json_dir = f'{STATS_ROOT_DIR}/{SRC2DST_JSON}'
    select_type = st.segmented_control("IP spec", ('IP Address', 'IP Link', 'Cross-country IP Link'), selection_mode='single')
    select_spec = st.segmented_control("heatmap type", ("Presence", "Density"), selection_mode='single')
    if not select_type or not select_spec:
        return
    prefix = f'{vp}2{dst}'
    if select_type == 'Cross-country IP Link':
        prefix += '_crosscn_edge'
    else:
        if select_type == 'IP Link':
            prefix += '_edge'
        else:
            prefix += '_node'
    ref = None
    for data in os.listdir(json_dir):
        if data.startswith(prefix):
            ref = data

    if not ref:
        st.write(f'unable to find data for {select_type}, {select_spec} for {vp}2{dst} in {json_dir}')
    else:
        start_time = select_start.strftime('%y-%m-%d')
        end_time = select_end.strftime('%y-%m-%d')
        contiguous_flag = True if select_contiguous else False
        fig1, _ = processor(os.path.join(json_dir, ref), start_time, end_time,
            contiguous_flag = contiguous_flag, mode=select_spec.lower())
        start_str = select_start.strftime('%m-%d')
        end_str = select_end.strftime('%m-%d')
        type_str = '_'.join(select_type.lower().split())
        spec_str = select_spec.lower()
        savefig_button(fig1, f'{vp}2{dst}-{start_str}-to-{end_str}', f'vis_{type_str}_{spec_str}_heatmap.png')
        st.pyplot(fig1)
 
