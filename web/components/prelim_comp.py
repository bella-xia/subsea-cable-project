import streamlit as st
from utils.constants import ROOT_DIR, DATA_ROOT_DIR, SRC2DST_RAW
from utils.utils import extract_stats_images
from .reusable_comp import render_button
import os, datetime

def render_prelim_img(select_src, select_dst):
    if not select_src or not select_dst:
        return

    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[0]
    img_dir = f'{ROOT_DIR}/{vp}2{dst}'
    img_dict = extract_stats_images(img_dir)
    hop_rtt_img, stophop_imgs = img_dict.get('Hop Num and RTT'), sorted(img_dict['Stop Hop Reasons'])
    res = (st.image(hop_rtt_img) if hop_rtt_img else st.markdown(
            f'no round-trip time data from {vp} to {dst}'))
    res = (st.image(stophop_imgs[st.session_state.img_idx]) if len(stophop_imgs) > 0 else st.markdown(
            f'no stop hot reason data from {vp} to {dst}'))
    render_button(len(stophop_imgs))

def render_prelim_realtime(select_src, select_dst, select_start, select_end, 
    select_contiguous, processor=None):
    if not select_src or not select_dst or not processor:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    img_dir = f'{DATA_ROOT_DIR}/{SRC2DST_RAW}'
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
        st.pyplot(figs[st.session_state.img_idx])
        render_button(3) 


