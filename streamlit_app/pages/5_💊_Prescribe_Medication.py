from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from app.api_client import EPRClientError, UnauthorizedError
from app.session import add_activity, init_session_state, require_auth


st.set_page_config(page_title="Prescribe Medication", page_icon="💊", layout="wide")
init_session_state()
require_auth()

patient = st.session_state.selected_patient
if not patient:
    st.warning("No patient selected. Please search for a patient first.")
    if st.button("Go to Patient Lookup"):
        st.switch_page("pages/2_🔍_Patient_Lookup.py")
    st.stop()

client = st.session_state.api_client

common_meds = [
    "Olanzapine",
    "Quetiapine",
    "Risperidone",
    "Aripiprazole",
    "Clozapine",
    "Metformin",
    "Atorvastatin",
    "Simvastatin",
    "Other (custom)",
]

st.title("💊 Prescribe Medication")
st.caption(f"Patient: {patient['pseudonym']} ({patient['sex']}, {patient['age_band']})")

with st.form("add_medication"):
    med_choice = st.selectbox("Drug Name", options=common_meds)
    custom_name = st.text_input("Custom Drug Name", disabled=(med_choice != "Other (custom)"))
    dose = st.text_input("Dose")
    start_date = st.date_input("Start Date", value=date.today())
    include_stop = st.checkbox("Add Stop Date")
    stop_date = st.date_input("Stop Date", value=date.today(), disabled=not include_stop)
    submitted = st.form_submit_button("Prescribe Medication", type="primary")

if submitted:
    drug_name = custom_name.strip() if med_choice == "Other (custom)" else med_choice
    if not drug_name:
        st.error("Drug name is required.")
    elif not dose.strip():
        st.error("Dose is required.")
    elif start_date > date.today():
        st.error("Start date cannot be in the future.")
    elif include_stop and stop_date < start_date:
        st.error("Stop date must be after start date.")
    else:
        start_dt = datetime.combine(start_date, datetime.min.time()).isoformat()
        stop_dt = datetime.combine(stop_date, datetime.min.time()).isoformat() if include_stop else None
        with st.spinner("Saving medication..."):
            try:
                created = client.create_medication(
                    patient_id=patient["id"],
                    drug_name=drug_name,
                    dose=dose.strip(),
                    start_date=start_dt,
                    stop_date=stop_dt,
                )
                add_activity(f"{patient['pseudonym']}: {created['drug_name']} prescribed")
                st.success("Medication prescribed.")
                st.switch_page("pages/3_👤_Patient_Record.py")
            except UnauthorizedError:
                st.warning("Session expired. Please log in again.")
                st.switch_page("pages/1_🔐_Login.py")
            except EPRClientError as exc:
                st.error(str(exc))

st.divider()
st.subheader("Common Antipsychotics")
st.write("- Olanzapine (typical dose: 5-20mg)")
st.write("- Quetiapine (typical dose: 150-750mg)")
st.write("- Risperidone (typical dose: 2-6mg)")
st.write("- Aripiprazole (typical dose: 10-30mg)")
st.write("- Clozapine (typical dose: 200-450mg)")

