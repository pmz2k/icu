from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from app.api_client import EPRClientError, UnauthorizedError
from app.session import add_activity, init_session_state, require_auth


st.set_page_config(page_title="Add Test Result", page_icon="📊", layout="wide")
init_session_state()
require_auth()

patient = st.session_state.selected_patient
if not patient:
    st.warning("No patient selected. Please search for a patient first.")
    if st.button("Go to Patient Lookup"):
        st.switch_page("pages/2_🔍_Patient_Lookup.py")
    st.stop()

client = st.session_state.api_client

test_types = {
    "HbA1c": {"unit": "mmol/mol", "description": "Diabetes screening"},
    "Weight": {"unit": "kg", "description": "Body weight"},
    "ECG": {"unit": "ms", "description": "QTc interval"},
    "FBC": {"unit": "x10^9/L", "description": "Full blood count"},
    "LFT": {"unit": "U/L", "description": "Liver function test"},
}

st.title("📊 Add Test Result")
st.caption(f"Patient: {patient['pseudonym']} ({patient['sex']}, {patient['age_band']})")

with st.form("add_observation"):
    test_type = st.selectbox("Test Type", options=list(test_types.keys()))
    value = st.number_input("Value", value=0.0, step=0.1, format="%.2f")
    unit = test_types[test_type]["unit"]
    st.text_input("Unit", value=unit, disabled=True)
    performed_on = st.date_input("Date Performed", value=date.today())
    interpretation = st.selectbox("Interpretation", options=["NORMAL", "ABNORMAL", "CRITICAL"])
    submitted = st.form_submit_button("Add Test Result", type="primary")

if submitted:
    if performed_on > date.today():
        st.error("Date performed cannot be in the future.")
    else:
        performed_dt = datetime.combine(performed_on, datetime.min.time()).isoformat()
        with st.spinner("Saving test result..."):
            try:
                created = client.create_observation(
                    patient_id=patient["id"],
                    obs_type=test_type,
                    value=float(value),
                    unit=unit,
                    interpretation=interpretation,
                    performed_date=performed_dt,
                )
                add_activity(f"{patient['pseudonym']}: {created['type']} added")
                st.success("Test result added.")
                st.switch_page("pages/3_👤_Patient_Record.py")
            except UnauthorizedError:
                st.warning("Session expired. Please log in again.")
                st.switch_page("pages/1_🔐_Login.py")
            except EPRClientError as exc:
                st.error(str(exc))

st.divider()
st.subheader("Test Type Reference")
for name, meta in test_types.items():
    st.write(f"- **{name}**: {meta['description']} ({meta['unit']})")

