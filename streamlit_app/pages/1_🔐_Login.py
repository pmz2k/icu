from __future__ import annotations

import streamlit as st

from app.api_client import EPRClientError
from app.session import init_session_state


st.set_page_config(page_title="EPR Login", page_icon="🔐", layout="centered")
init_session_state()

if st.session_state.token:
    st.info("You are already logged in.")
    if st.button("Go to Dashboard"):
        st.switch_page("Home.py")
    st.stop()

st.title("🏥 EPR System Login")
st.write("Please log in to access the Electronic Patient Record system.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login", type="primary", use_container_width=True):
    if not username or not password:
        st.warning("Please enter username and password.")
    else:
        with st.spinner("Authenticating..."):
            try:
                result = st.session_state.api_client.login(username, password)
                st.session_state.token = result["access_token"]
                st.session_state.user = result["user"]
                st.success("Login successful.")
                st.switch_page("Home.py")
            except EPRClientError as exc:
                st.error(f"Login failed: {exc}")

with st.expander("Test Credentials"):
    st.info(
        "Clinician: clinician / password123\n\n"
        "Admin: admin / admin123"
    )

