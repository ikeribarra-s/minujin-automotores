import os
import httpx
import streamlit as st
from typing import Any
from dotenv import load_dotenv

load_dotenv()
_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle(response: httpx.Response) -> Any:
    if response.status_code == 204:
        return None
    response.raise_for_status()
    return response.json()


def get(path: str, **params) -> Any:
    with httpx.Client(base_url=_BASE_URL) as client:
        return _handle(client.get(path, params=params, headers=_headers()))


def post(path: str, data: dict) -> Any:
    with httpx.Client(base_url=_BASE_URL) as client:
        return _handle(client.post(path, json=data, headers=_headers()))


def put(path: str, data: dict) -> Any:
    with httpx.Client(base_url=_BASE_URL) as client:
        return _handle(client.put(path, json=data, headers=_headers()))


def patch(path: str, data: dict) -> Any:
    with httpx.Client(base_url=_BASE_URL) as client:
        return _handle(client.patch(path, json=data, headers=_headers()))


def delete(path: str) -> None:
    with httpx.Client(base_url=_BASE_URL) as client:
        _handle(client.delete(path, headers=_headers()))


def upload_file(path: str, file_bytes: bytes, filename: str, content_type: str, timeout: float = 120.0) -> Any:
    with httpx.Client(base_url=_BASE_URL, timeout=timeout) as client:
        return _handle(client.post(
            path,
            files={"file": (filename, file_bytes, content_type)},
            headers=_headers(),
        ))


def login(username: str, password: str) -> bool:
    try:
        with httpx.Client(base_url=_BASE_URL) as client:
            r = client.post("/auth/token", data={"username": username, "password": password})
            r.raise_for_status()
            st.session_state["token"] = r.json()["access_token"]
            return True
    except httpx.HTTPStatusError:
        return False
