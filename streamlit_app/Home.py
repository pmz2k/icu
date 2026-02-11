from __future__ import annotations

from datetime import date

import streamlit as st

from app.api_client import EPRClientError, UnauthorizedError
from app.session import get_known_patients, init_session_state, logout, require_auth


st.set_page_config(page_title="NHS Mock EPR", page_icon="🏥", layout="wide")
init_session_state()
require_auth()

user = st.session_state.user or {}
client = st.session_state.api_client

left, right = st.columns([5, 1])
with left:
    st.title("🏥 NHS Mock Electronic Patient Record System")
    st.caption("Clinician-facing interface for pseudonymised EPR data")
with right:
    if st.button("Log out", type="secondary", use_container_width=True):
        logout()

st.markdown(f"Welcome, **{user.get('full_name', 'User')}** ({user.get('role', 'clinician').title()})")

known_patients = get_known_patients()
today_tests = 0
if st.session_state.selected_patient:
    try:
        observations = client.get_observations(st.session_state.selected_patient["id"])
        today_key = date.today().isoformat()
        today_tests = sum(1 for obs in observations if str(obs.get("performed_date", "")).startswith(today_key))
    except (UnauthorizedError, EPRClientError):
        today_tests = 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Patients (session)", len(known_patients))
col2.metric("Tests Today (selected patient)", today_tests)
col3.metric("Exports Pending", 0)

st.subheader("Quick Actions")
q1, q2, q3, q4 = st.columns(4)
if q1.button("🔍 Search Patient", use_container_width=True):
    st.switch_page("pages/2_🔍_Patient_Lookup.py")
if q2.button("📊 Add Test Result", use_container_width=True):
    st.switch_page("pages/4_📊_Add_Test_Result.py")
if q3.button("💊 Prescribe Medication", use_container_width=True):
    st.switch_page("pages/5_💊_Prescribe_Medication.py")
if q4.button("📥 Export Data", use_container_width=True):
    st.switch_page("pages/6_📥_Export_Data.py")

st.subheader("Recent Activity")
if st.session_state.activity_log:
    for item in st.session_state.activity_log[:8]:
        st.write(f"- {item['message']} ({item['timestamp']})")
else:
    st.info("No activity yet in this session.")

st.subheader("System Status")
try:
    health = client.health_check()
    st.success(
        f"Connected to EPR API: {health.get('status', 'unknown')} "
        f"(v{health.get('version', 'n/a')} - {health.get('response_ms', 0)} ms)"
    )
except EPRClientError as exc:
    st.error(f"API status check failed: {exc}")

