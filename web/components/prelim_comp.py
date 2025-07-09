import streamlit as st
from utils.constants import ROOT_DIR
from utils.utils import extract_stats_images
from .reusable_comp import render_button

def render_prelim(select_src, select_dst):
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

