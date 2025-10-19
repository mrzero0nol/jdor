import os
import requests
import uuid
from datetime import datetime, timezone, timedelta

BASE_CIAM_URL = os.getenv("BASE_CIAM_URL")
BASIC_AUTH = os.getenv("BASIC_AUTH")
UA = os.getenv("UA")

# Variabel ini perlu didefinisikan di sini karena tidak dapat diimpor
# dari engsel.py karena dependensi melingkar.
AX_DEVICE_ID = None
AX_FP = None

def set_global_ax_vars(device_id, fp):
    global AX_DEVICE_ID, AX_FP
    AX_DEVICE_ID = device_id
    AX_FP = fp

def get_new_token(refresh_token: str) -> dict | None:
    if not AX_DEVICE_ID or not AX_FP:
        raise ValueError("AX_DEVICE_ID and AX_FP must be set using set_global_ax_vars")

    url = f"{BASE_CIAM_URL}/realms/xl-ciam/protocol/openid-connect/token"

    now = datetime.now(timezone(timedelta(hours=7)))
    ax_request_at = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0700"
    ax_request_id = str(uuid.uuid4())

    headers = {
        "Host": BASE_CIAM_URL.replace("https://", ""),
        "ax-request-at": ax_request_at,
        "ax-device-id": AX_DEVICE_ID,
        "ax-request-id": ax_request_id,
        "ax-request-device": "samsung",
        "ax-request-device-model": "SM-N935F",
        "ax-fingerprint": AX_FP,
        "authorization": f"Basic {BASIC_AUTH}",
        "user-agent": UA,
        "ax-substype": "PREPAID",
        "content-type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)

        if resp.status_code == 400 and resp.json().get("error_description") == "Session not active":
            print("Refresh token expired. Please re-add the account.")
            return None

        resp.raise_for_status()
        body = resp.json()

        if "id_token" not in body or "error" in body:
            error_msg = body.get('error_description', 'No error description')
            print(f"Error in token response: {error_msg}")
            return None

        return body
    except requests.RequestException as e:
        print(f"Failed to get new token: {e}")
        return None
