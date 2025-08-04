import streamlit as st
from utils.constants import STATS_ROOT_DIR, SRC2DST_RAW
from utils.utils import extract_stats_images
from .reusable_comp import render_button, savefig_button
import os, datetime

def render_prelim_realtime(select_src, select_dst, select_start, select_end, 
    select_contiguous, processor=None):
    if not select_src or not select_dst or not processor:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    img_dir = f'{STATS_ROOT_DIR}/{SRC2DST_RAW}'
    ref = None
    for data in os.listdir(img_dir):
        if data.startswith(f'{vp}2{dst}'):
            ref = data
            break
    
    if not ref:
        st.write(f'did not find data from {vp} to {dst} inside collective dir: {img_dir}')
    else:
        start_time = 'xx' if not select_start else select_start.strftime('%y-%m-%d')
        end_time = 'xx' if not select_end else select_end.strftime('%y-%m-%d')
        contiguous_flag = True if select_contiguous else False
        figs = processor(os.path.join(img_dir, ref), start_time, end_time, contiguous_flag=contiguous_flag)
        start_str = select_start.strftime('%m-%d')
        end_str = select_end.strftime('%m-%d')
        savefig_button(figs[st.session_state.img_idx], f'{vp}2{dst}-{start_str}-to-{end_str}', f'vis_prelim_idx{st.session_state.img_idx}.png')
        st.pyplot(figs[st.session_state.img_idx])
        render_button(3) 


