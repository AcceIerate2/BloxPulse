from src.utility import lock, dataFilePath
from src.notificationHandler import pushNotification
import warnings, json, time

from typing import TypedDict
class ReceivedData(TypedDict):
    universeId: str # straight forward
    notificationId: str # assetid for notifications
    key: str # userid
    time: int # set the exact time (that unix epoch thingy)
    message: str # messsage to send
    api_key: str

def loop_scheduler():
    print("Running!")
    
    while True: 
        due_list = []

        with lock:
            try:
                with open(f"{dataFilePath}", "r", encoding="utf-8") as f:
                    fileContent = json.load(f)
            except:
                warnings.warn("Could not load data.json file!")
                fileContent = {}

            currentTime = int(time.time())

            for universeId, universeNotifications in list(fileContent.items()):
                if not isinstance(universeNotifications, dict): 
                    continue

                for key in list(universeNotifications.keys()):
                    notificationData: ReceivedData = universeNotifications.get(key)
                    if not isinstance(notificationData, dict): 
                        continue

                    try:
                        deadline = int(notificationData.get("time"))
                    except:
                        continue

                    if currentTime >= deadline:
                        due_list.append((universeId, key, notificationData))
                        universeNotifications.pop(key, None)

            with open(f"{dataFilePath}", "w", encoding="utf-8") as f:
                json.dump(fileContent, f, indent=2, ensure_ascii=False)

        for uni_id, key, entry in due_list:
            try:
                pushNotification(entry)
                print(f"Pushed Notification: universeId={uni_id}, key={key}")
            except Exception as e:
                warnings.warn(f"Notification failed {uni_id}/{key}: {e}", RuntimeWarning)

        time.sleep(60)

if __name__ == "__main__":
    loop_scheduler()
