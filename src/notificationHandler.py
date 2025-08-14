import requests
from typing import TypedDict
from .. import config

URL_ENDPOINT = config.URL_ENDPOINT
API_KEY = config.API_KEY

class ReceivedData(TypedDict):
    universeId: str       # straight forward
    notificationId: str   # assetId for notifications
    key: str              # userId
    time: int             # unix epoch
    message: str          # message to send

def pushNotification(data: ReceivedData):
    """
    Sends a Roblox cloud notification to the user in data['key'].
    """
    user_id = data["key"]  # userId from JSON

    url = f"{URL_ENDPOINT}/users/{user_id}/notifications"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "source": {
            "universe": f"universes/{data['universeId']}"
        },
        "payload": {
            "message_id": data["notificationId"],  # assetId
            "type": "MOMENT"
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)

        print(resp.status_code)

        resp.raise_for_status()
        return {
            "status": "success",
            "code": resp.status_code,
            "body": resp.json()
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }
