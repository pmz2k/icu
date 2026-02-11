from __future__ import annotations

import re

import streamlit as st

from app.api_client import EPRClientError, NotFoundError, UnauthorizedError
from app.session import add_activity, init_session_state, remember_patient, require_auth


st.set_page_config(page_title="Patient Lookup", page_icon="🔍", layout="wide")
init_session_state()
require_auth()

client = st.session_state.api_client

st.title("🔍 Patient Lookup")

with st.form("patient_search"):
    nhs_number = st.text_input("NHS Number", max_chars=10, help="Enter 10-digit NHS number.")
    search = st.form_submit_button("Search", type="primary")

found_patient = None
show_register = False

if search:
    if not re.fullmatch(r"\d{10}", nhs_number or ""):
        st.error("NHS number must be exactly 10 digits.")
    else:
        with st.spinner("Searching patient..."):
            try:
                found_patient = client.get_patient_by_nhs(nhs_number)
                remember_patient(found_patient)
                add_activity(f"{found_patient['pseudonym']}: Patient record opened")
                st.success("Patient found.")
            except NotFoundError:
                show_register = True
                st.warning("Patient not found. You can register a new patient below.")
            except UnauthorizedError:
                st.warning("Session expired. Please log in again.")
                st.switch_page("pages/1_🔐_Login.py")
                st.stop()
            except EPRClientError as exc:
                st.error(str(exc))

patient = found_patient or st.session_state.selected_patient
if patient:
    st.subheader("Patient Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pseudonymous ID", patient["pseudonym"])
    c2.metric("Sex", patient["sex"])
    c3.metric("Age Band", patient["age_band"])
    c4.metric("Registered", str(patient["created_at"])[:10])

    a1, a2, a3 = st.columns(3)
    if a1.button("View Full Record", use_container_width=True):
        st.switch_page("pages/3_👤_Patient_Record.py")
    if a2.button("Add Test Result", use_container_width=True):
        st.switch_page("pages/4_📊_Add_Test_Result.py")
    if a3.button("Prescribe Medication", use_container_width=True):
        st.switch_page("pages/5_💊_Prescribe_Medication.py")

if show_register:
    st.divider()
    st.subheader("📝 Register New Patient")
    sex_map = {"Male": "M", "Female": "F", "Other": "Other"}
    with st.form("register_patient"):
        sex_choice = st.selectbox("Sex", options=list(sex_map.keys()))
        age_band = st.selectbox("Age Band", options=["18-25", "26-35", "36-45", "46-55", "56-65", "66-75", "76+"])
        register = st.form_submit_button("Register Patient", type="primary")

    if register:
        with st.spinner("Registering patient..."):
            try:
                created = client.create_patient(nhs_number=nhs_number, sex=sex_map[sex_choice], age_band=age_band)
                remember_patient(created)
                add_activity(f"{created['pseudonym']}: Patient registered")
                st.success(f"Patient registered: {created['pseudonym']}")
                st.switch_page("pages/3_👤_Patient_Record.py")
            except EPRClientError as exc:
                st.error(str(exc))

