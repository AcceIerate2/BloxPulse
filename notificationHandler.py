import requests
from typing import TypedDict
import config

API_ENDPOINT = config.API_ENDPOINT

class ReceivedData(TypedDict):
    universeId: str       # straight forward
    notificationId: str   # assetId for notifications
    key: str              # userId
    time: int             # unix epoch
    message: str          # message to send
    api_key: str

def pushNotification(data: ReceivedData):
    """
    Sends a Roblox cloud notification to the user in data['key'].
    """
    user_id = str.split(str(data["key"]), "_")[0]  

    url = f"{API_ENDPOINT}/users/{user_id}/notifications"

    headers = {
        "x-api-key": data["api_key"],
        "Content-Type": "application/json"
    }

    payload = {
        "source": {
            "universe": f"universes/{data['universeId']}"
        },
        "payload": {
            "type": "MOMENT",                    
            "messageId": str.split(str(data["notificationId"]), "_")[0],  
            "parameters": {
                "text": { "stringValue": data["message"] }  
            }
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)

        print(f"Status Code: {resp.status_code}, Pushing Notification to user: {data["key"]}, Message: {str(resp.text)}")

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
