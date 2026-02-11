from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from app.api_client import EPRClientError, UnauthorizedError
from app.session import add_activity, init_session_state, require_auth


st.set_page_config(page_title="Patient Record", page_icon="👤", layout="wide")
init_session_state()
require_auth()

patient = st.session_state.selected_patient
if not patient:
    st.warning("No patient selected. Search for a patient first.")
    if st.button("Go to Patient Lookup"):
        st.switch_page("pages/2_🔍_Patient_Lookup.py")
    st.stop()

client = st.session_state.api_client
st.title(f"👤 Patient Record: {patient['pseudonym']}")

demo1, demo2, demo3, demo4 = st.columns(4)
demo1.metric("Pseudonym", patient["pseudonym"])
demo2.metric("Age Band", patient["age_band"])
demo3.metric("Sex", patient["sex"])
demo4.metric("Registered", str(patient["created_at"])[:10])

try:
    meds = client.get_medications(patient["id"])
    obs = client.get_observations(patient["id"])
except UnauthorizedError:
    st.warning("Session expired. Please log in again.")
    st.switch_page("pages/1_🔐_Login.py")
    st.stop()
except EPRClientError as exc:
    st.error(f"Unable to load record: {exc}")
    st.stop()

tabs = st.tabs(["💊 Medications", "📊 Test Results"])

with tabs[0]:
    if meds:
        med_rows = []
        today = date.today().isoformat()
        for m in meds:
            stop = str(m.get("stop_date") or "")
            is_active = (not stop) or (stop[:10] >= today)
            med_rows.append(
                {
                    "Drug": m["drug_name"],
                    "Dose": m["dose"],
                    "Started": str(m["start_date"])[:10],
                    "Stopped": stop[:10] if stop else "",
                    "Status": "🟢 Active" if is_active else "⚪ Stopped",
                }
            )
        st.dataframe(pd.DataFrame(med_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No medications recorded for this patient.")

with tabs[1]:
    if obs:
        flag = {"NORMAL": "🟢 NORMAL", "ABNORMAL": "🟠 ABNORMAL", "CRITICAL": "🔴 CRITICAL"}
        obs_rows = [
            {
                "Date": str(o["performed_date"])[:10],
                "Test": o["type"],
                "Value": o["value"],
                "Unit": o["unit"],
                "Status": flag.get(o.get("interpretation", ""), o.get("interpretation", "")),
            }
            for o in obs
        ]
        df = pd.DataFrame(obs_rows).sort_values("Date", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No observations recorded for this patient.")

b1, b2, b3, b4 = st.columns(4)
if b1.button("➕ Add Test", use_container_width=True):
    st.switch_page("pages/4_📊_Add_Test_Result.py")
if b2.button("💊 Prescribe", use_container_width=True):
    st.switch_page("pages/5_💊_Prescribe_Medication.py")
if b3.button("📥 Export Data", use_container_width=True):
    st.switch_page("pages/6_📥_Export_Data.py")
if b4.button("🔄 Refresh", use_container_width=True):
    add_activity(f"{patient['pseudonym']}: Record refreshed")
    st.rerun()

