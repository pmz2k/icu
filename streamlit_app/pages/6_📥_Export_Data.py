from __future__ import annotations

import tempfile
from datetime import datetime

import streamlit as st

from app.api_client import EPRClientError, UnauthorizedError
from app.session import get_known_patients, init_session_state, require_auth


st.set_page_config(page_title="Export Data", page_icon="📥", layout="wide")
init_session_state()
require_auth()

client = st.session_state.api_client
known_patients = get_known_patients()
selected = st.session_state.selected_patient

st.title("📥 Export Patient Data")

mode = st.radio("Export Options", options=["Single Patient", "All Patients"], horizontal=True)

patient_id = None
patient_label = "All Patients"
if mode == "Single Patient":
    options = []
    if selected:
        options.append(selected)
    options.extend([p for p in known_patients if not selected or p["id"] != selected["id"]])
    if not options:
        st.warning("No patient available in session. Search for a patient first.")
    else:
        option_map = {f"{p['pseudonym']} ({p['age_band']}, {p['sex']})": p for p in options}
        picked_label = st.selectbox("Patient", options=list(option_map.keys()))
        picked = option_map[picked_label]
        patient_id = picked["id"]
        patient_label = picked["pseudonym"]

if st.button("Generate Export", type="primary", disabled=(mode == "Single Patient" and patient_id is None)):
    with st.spinner("Generating export..."):
        try:
            job_id = client.export_csv(patient_id=patient_id)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                save_path = tmp.name
            client.download_csv(job_id, save_path)
            with open(save_path, "rb") as fh:
                zip_bytes = fh.read()

            st.session_state.exports.insert(
                0,
                {
                    "job_id": job_id,
                    "label": patient_label,
                    "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    "bytes": zip_bytes,
                },
            )
            st.session_state.exports = st.session_state.exports[:10]

            st.success(f"Export generated. Job ID: {job_id}")
            st.download_button(
                label="📥 Download Export",
                data=zip_bytes,
                file_name=f"epr_export_{job_id}.zip",
                mime="application/zip",
                key=f"download_current_{job_id}",
            )
        except UnauthorizedError:
            st.warning("Session expired. Please log in again.")
            st.switch_page("pages/1_🔐_Login.py")
            st.stop()
        except EPRClientError as exc:
            st.error(str(exc))

st.divider()
st.subheader("Export Contents")
st.write("- patients.csv (demographics)")
st.write("- medications.csv (prescriptions)")
st.write("- events.csv (test results)")
st.info("Data protection: exports contain pseudonymous IDs only. NHS numbers are never included.")

st.divider()
st.subheader("Recent Exports")
if st.session_state.exports:
    for idx, item in enumerate(st.session_state.exports):
        col1, col2 = st.columns([4, 1])
        col1.write(f"✅ Export #{item['job_id']} - {item['label']} - {item['created_at']}")
        col2.download_button(
            label="Download",
            data=item["bytes"],
            file_name=f"epr_export_{item['job_id']}.zip",
            mime="application/zip",
            key=f"download_hist_{idx}_{item['job_id']}",
        )
else:
    st.info("No exports generated in this session.")

