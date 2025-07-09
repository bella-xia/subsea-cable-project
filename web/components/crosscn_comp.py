import streamlit as st
import os
from utils.constants import ROOT_DIR, ASN_SUBDIR
from utils.utils import reset_page
from .reusable_comp import render_button


def render_crosscn_asn(select_src):
    if not select_src:
        return

    vp = select_src.split('-')[1]
    img_dir = f'{ROOT_DIR}/{ASN_SUBDIR}/{vp}-crosscn-asn'
    airport_set = set()
    for f in os.listdir(img_dir):
        airport_set.add(f.split('-')[0])

    select_airport = st.selectbox(
        'selected airport',
        tuple(airport_set),
        index=0,
        placeholder='select an airport',
        on_change=reset_page)
    img_dir += f'/{select_airport}-{vp}-maxmind-front-as'
    imgs =  sorted(os.listdir(img_dir))
    st.image(os.path.join(img_dir, imgs[st.session_state.img_idx]), use_container_width=True)
    render_button(len(imgs))

