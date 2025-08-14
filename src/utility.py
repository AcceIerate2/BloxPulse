from filelock import FileLock
import json

dataFilePath = "../data.json"

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
    
    return None, 200

def writeToFile(universeId: str, referenceId: str, data: dict):
    if type(universeId) != str or type(referenceId) != str: 
        return

    lock = FileLock(dataFilePath)
    with lock:
        with open(dataFilePath, "r") as f:
            fileContent = json.load(f)

        if not fileContent[universeId]:
            fileContent[universeId] = {}

        if fileContent[universeId][referenceId]:
            return
        
        fileContent[universeId][referenceId] = data
        with open(dataFilePath, "w") as f:
            json.dump(fileContent, f, indent=4)

        f.close()
    
def removeFromFile(universeId: str, referenceId: str):
    if type(universeId) != str or type(referenceId) != str: 
        return

    lock = FileLock(dataFilePath)
    with lock:
        with open(dataFilePath, "r") as f:
            fileContent = json.load(f)

        if not fileContent[universeId]: 
            return

        if fileContent[universeId][referenceId]:
            del fileContent[referenceId]
        
        with open(dataFilePath, "w") as f:
            json.dump(fileContent, f, indent=4)

        f.close()