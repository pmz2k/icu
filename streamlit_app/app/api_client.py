from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class EPRClientError(Exception):
    """Base client error with user-friendly message."""


class UnauthorizedError(EPRClientError):
    """Raised when API token is missing/expired."""


class NotFoundError(EPRClientError):
    """Raised when a resource is not found."""


class EPRClient:
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: Optional[str] = None
        self.session = requests.Session()

    def set_token(self, token: Optional[str]) -> None:
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
        retries: int = 2,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        if auth_required and not self.token:
            raise UnauthorizedError("Session expired. Please log in again.")

        attempt = 0
        while True:
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    headers=self._headers(),
                    params=params,
                    json=json,
                    data=data,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                if attempt < retries:
                    attempt += 1
                    time.sleep(0.5 * attempt)
                    continue
                raise EPRClientError("Could not connect to EPR API. Please try again.") from exc

            if resp.status_code == 401:
                raise UnauthorizedError("Your session is no longer valid. Please log in again.")
            if resp.status_code == 404:
                raise NotFoundError("Requested record was not found.")
            if resp.status_code >= 500:
                if attempt < retries:
                    attempt += 1
                    time.sleep(0.5 * attempt)
                    continue
                raise EPRClientError("EPR server error. Please retry in a moment.")
            if resp.status_code >= 400:
                detail = ""
                try:
                    body = resp.json()
                    detail = body.get("detail", "")
                except ValueError:
                    detail = resp.text
                detail = str(detail).strip() or "Request failed."
                raise EPRClientError(detail)
            return resp

    def login(self, username: str, password: str) -> Dict[str, Any]:
        token_resp = self._request(
            "POST",
            "/oauth/token",
            auth_required=False,
            data={"username": username, "password": password},
        )
        token_body = token_resp.json()
        access_token = token_body["access_token"]
        self.set_token(access_token)

        user_resp = self._request("GET", "/oauth/userinfo")
        user = user_resp.json()
        return {"access_token": access_token, "token_type": token_body.get("token_type", "bearer"), "user": user}

    def get_patient_by_nhs(self, nhs_number: str) -> Optional[Dict[str, Any]]:
        resp = self._request("GET", "/Patient", params={"identifier": nhs_number})
        return resp.json()

    def create_patient(self, nhs_number: str, sex: str, age_band: str) -> Dict[str, Any]:
        resp = self._request("POST", "/Patient", json={"nhs_number": nhs_number, "sex": sex, "age_band": age_band})
        return resp.json()

    def get_observations(self, patient_id: str) -> List[Dict[str, Any]]:
        resp = self._request("GET", "/Observation", params={"patient": patient_id})
        return resp.json()

    def create_observation(
        self,
        patient_id: str,
        obs_type: str,
        value: float,
        unit: str,
        interpretation: str,
        performed_date: str,
    ) -> Dict[str, Any]:
        payload = {
            "patient_id": patient_id,
            "type": obs_type,
            "value": value,
            "unit": unit,
            "interpretation": interpretation,
            "performed_date": performed_date,
        }
        resp = self._request("POST", "/Observation", json=payload)
        return resp.json()

    def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        resp = self._request("GET", "/MedicationRequest", params={"patient": patient_id})
        return resp.json()

    def create_medication(
        self,
        patient_id: str,
        drug_name: str,
        dose: str,
        start_date: str,
        stop_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "patient_id": patient_id,
            "drug_name": drug_name,
            "dose": dose,
            "start_date": start_date,
        }
        if stop_date:
            payload["stop_date"] = stop_date
        resp = self._request("POST", "/MedicationRequest", json=payload)
        return resp.json()

    def export_csv(self, patient_id: Optional[str] = None) -> str:
        params = {"patient_id": patient_id} if patient_id else None
        resp = self._request("POST", "/export/csv", params=params)
        return resp.json()["id"]

    def download_csv(self, job_id: str, save_path: str) -> None:
        resp = self._request("GET", f"/export/csv/{job_id}")
        target = Path(save_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(resp.content)

    def simulate_events(self, patient_id: str, count: int = 10) -> Dict[str, Any]:
        resp = self._request("POST", "/simulate/events", params={"patient_id": patient_id, "count": count})
        return resp.json()

    def health_check(self) -> Dict[str, Any]:
        started = time.perf_counter()
        resp = self._request("GET", "/health", auth_required=False, retries=0)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        payload = resp.json()
        payload["response_ms"] = elapsed_ms
        return payload

