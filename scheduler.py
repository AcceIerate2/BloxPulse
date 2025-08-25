databaseUrl = "https://bloxpulsedbserver.pythonanywhere.com/"

from notificationHandler import pushNotification
import warnings, time, requests
from threading import Thread

from typing import TypedDict
class ReceivedData(TypedDict):
    universeId: str 
    notificationId: str 
    key: str
    time: int 
    message: str
    api_key: str 
    
def startPushing():
    print("🚨 Preparing to push notifications!")

    response = requests.get(f"{databaseUrl}get_database")
    if response.status_code != 200:
        return
    
    database: list = response.json()
    if not isinstance(database, list):
        return

    now = int(time.time())

    due = []
    for data in database:
        _time = int(data["time"])

        if now < _time:
            continue
        
        pushNotification(data)
        
        universeId = data["universeId"]
        if not universeId: 
            continue

        due.append(data)

    success = False
    for _ in range(3):
        try:
            statusCode = requests.post(f"{databaseUrl}bulk_remove", json=due)
            if statusCode.status_code == 200:
                success = True
                break
        except requests.exceptions.RequestException as m: 
            time.sleep(1)
            continue

    if success == False:
        warnings.warn("Could not bulk remove data!")

while True:
    time.sleep(120)
    startPushing()