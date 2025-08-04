import os
import streamlit as st
from utils.utils import prev_page, next_page

def render_button(total_len):
    if total_len > 0:
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.img_idx > 0:
                st.button("Prev Image", on_click=prev_page)
        with col2:
            if st.session_state.img_idx < total_len - 1:
                st.button("Next Image", on_click=next_page)


def savefig_button(fig, path_dir, img_name):
    os.makedirs(f'images/{path_dir}', exist_ok=True)
    path = f'images/{path_dir}/{img_name}'
    if st.button('SAVE FIGURE'):
        fig.savefig(path)
