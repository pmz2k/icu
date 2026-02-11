from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from app.api_client import EPRClient


def init_session_state() -> None:
    load_dotenv()

    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    if "known_patients" not in st.session_state:
        st.session_state.known_patients = []
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    if "exports" not in st.session_state:
        st.session_state.exports = []
    if "api_client" not in st.session_state:
        base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
        st.session_state.api_client = EPRClient(base_url=base_url)

    st.session_state.api_client.set_token(st.session_state.token)


def is_authenticated() -> bool:
    return bool(st.session_state.token)


def require_auth() -> None:
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.switch_page("pages/1_🔐_Login.py")
        st.stop()


def logout() -> None:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.selected_patient = None
    st.session_state.api_client.set_token(None)
    st.rerun()


def add_activity(message: str) -> None:
    st.session_state.activity_log.insert(
        0,
        {"message": message, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")},
    )
    st.session_state.activity_log = st.session_state.activity_log[:25]


def remember_patient(patient: Dict[str, Any]) -> None:
    existing = [p for p in st.session_state.known_patients if p.get("id") != patient.get("id")]
    st.session_state.known_patients = [patient] + existing
    st.session_state.known_patients = st.session_state.known_patients[:50]
    st.session_state.selected_patient = patient


def get_known_patients() -> List[Dict[str, Any]]:
    return st.session_state.known_patients

