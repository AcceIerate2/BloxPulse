import os, json
from filelock import FileLock

# Store file in /tmp instead of ../
DATA_DIR = "/tmp"
os.makedirs(DATA_DIR, exist_ok=True)
dataFilePath = os.path.join(DATA_DIR, "data.json")

# Make sure the file exists
if not os.path.exists(dataFilePath):
    with open(dataFilePath, "w") as f:
        json.dump({}, f)


def validData(receivedData):    
    if type(receivedData) != dict: 
        return {"error": "Invalid JSON"}, 400

    universeId = receivedData["universeId"]
    if type(universeId) != str:
        return {"error": "Invalid universeId"}, 400

    notificationId = receivedData["notificationId"]
    if type(notificationId) != str:
        return {"error": "Invalid notificationId"}, 400

    key = receivedData["key"]
    if type(key) != str: 
        return {"error": "Invalid key"}, 400
    
    time = receivedData["time"]
    if type(time) != int: 
        return {"error": "Invalid time"}, 400

    message = receivedData["message"]
    if type(message) != str:
        return {"error": "Invalid Message"}, 400

    api_key = receivedData["api_key"]
    if type(api_key) != str:
        return {"error": "Invalid api_key"}, 400

    return None, 200

def writeToFile(universeId: str, referenceId: str, data: dict):
    if not isinstance(universeId, str) or not isinstance(referenceId, str):
        return

    lock = FileLock(dataFilePath + ".lock")
    with lock:
        with open(dataFilePath, "r") as f:
            fileContent = json.load(f)

        # Ensure universeId dict exists
        if universeId not in fileContent:
            fileContent[universeId] = {}

        # Avoid overwriting if exists
        if referenceId in fileContent[universeId]:
            return

        fileContent[universeId][referenceId] = data

        with open(dataFilePath, "w") as f:
            json.dump(fileContent, f, indent=4)

    
def removeFromFile(universeId: str, referenceId: str):
    if not isinstance(universeId, str) or not isinstance(referenceId, str):
        return

    lock = FileLock(dataFilePath + ".lock")
    with lock:
        with open(dataFilePath, "r") as f:
            fileContent = json.load(f)

        if universeId not in fileContent:
            return

        if referenceId in fileContent[universeId]:
            del fileContent[universeId][referenceId]

        with open(dataFilePath, "w") as f:
            json.dump(fileContent, f, indent=4)
