from __future__ import annotations

import streamlit as st

from app.api_client import EPRClientError
from app.session import add_activity, get_known_patients, init_session_state, require_auth


st.set_page_config(page_title="Admin Tools", page_icon="⚙️", layout="wide")
init_session_state()
require_auth()

if (st.session_state.user or {}).get("role") != "admin":
    st.error("Admin access required.")
    st.stop()

client = st.session_state.api_client
known_patients = get_known_patients()
selected = st.session_state.selected_patient

st.title("⚙️ System Administration")

st.subheader("🧪 Test Data Generator")
generator_options = []
if selected:
    generator_options.append(selected)
generator_options.extend([p for p in known_patients if not selected or p["id"] != selected["id"]])

if generator_options:
    labels = {f"{p['pseudonym']} ({p['age_band']}, {p['sex']})": p for p in generator_options}
    selected_label = st.selectbox("Patient", options=list(labels.keys()))
    events_count = st.number_input("Number of Events", min_value=1, max_value=50, value=10, step=1)
    if st.button("Generate Test Data", type="primary"):
        patient = labels[selected_label]
        with st.spinner("Generating events..."):
            try:
                result = client.simulate_events(patient["id"], int(events_count))
                add_activity(f"{patient['pseudonym']}: {events_count} simulated events generated")
                st.success(result.get("message", "Events generated."))
            except EPRClientError as exc:
                st.error(str(exc))
else:
    st.info("No patient available in session. Search for a patient first.")

st.divider()
st.subheader("🔌 API Connection Test")
st.write(f"Endpoint: `{client.base_url}`")
if st.button("Test Connection"):
    try:
        health = client.health_check()
        st.success(
            f"Connected: {health.get('status', 'unknown')} | "
            f"Version {health.get('version', 'n/a')} | "
            f"{health.get('response_ms', 0)} ms"
        )
    except EPRClientError as exc:
        st.error(f"Connection failed: {exc}")

st.divider()
st.subheader("📊 System Statistics")
total_patients = len(known_patients)
total_exports = len(st.session_state.exports)
total_observations = 0
total_medications = 0
if selected:
    try:
        total_observations = len(client.get_observations(selected["id"]))
        total_medications = len(client.get_medications(selected["id"]))
    except EPRClientError:
        pass

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Total Patients (session)", total_patients)
s2.metric("Observations (selected patient)", total_observations)
s3.metric("Medications (selected patient)", total_medications)
s4.metric("Exports (session)", total_exports)
s5.metric("Database Size", "N/A")

