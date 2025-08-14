from flask import Flask, request
import requests
from src import utility
from filelock import FileLock
import json
import time
import threading
from src import notificationHandler

from src.utility import dataFilePath   # <-- import the SAME path the writer uses

from typing import TypedDict
class ReceivedData(TypedDict):
    universeId: str # straight forward
    notificationId: str # assetid for notifications
    key: str # userid
    time: int # set the exact time (that unix epoch thingy)
    message: str # messsage to send
    api_key: str

app = Flask(__name__)

def loop_scheduler():
    while True:
        lock = FileLock(f"{dataFilePath}.lock")
        with lock:
            # read
            with open(dataFilePath, "r") as f:
                fileContent = json.load(f)

            now = time.time()
            to_delete = []  # collect (uniId, refId) to delete after iter

            # iterate
            for uniId, parentEntry in list(fileContent.items()):
                if not isinstance(parentEntry, dict):
                    continue
                for refId, entry in list(parentEntry.items()):
                    if not isinstance(entry, dict):
                        continue
                    due_at = entry.get("time", 0)
                    if now >= due_at:
                        # send the notification using the entry payload
                        try:
                            notificationHandler.pushNotification(entry)
                            print(f"Push to {refId}: {entry.get('message')}")
                        except Exception as e:
                            print(f"Failed to push {refId}: {e}")
                            # optionally continue without deleting so it retries next tick
                        else:
                            to_delete.append((uniId, refId))

            # apply deletions
            for uniId, refId in to_delete:
                if uniId in fileContent and refId in fileContent[uniId]:
                    del fileContent[uniId][refId]
                    # clean up empty universe buckets
                    if not fileContent[uniId]:
                        del fileContent[uniId]

            # write once
            with open(dataFilePath, "w") as f:
                json.dump(fileContent, f, indent=4)

        time.sleep(1)


threading.Thread(target=loop_scheduler).start()

@app.route("/Schedule", methods=["POST"])
def Schedule():
    receivedData = request.get_json(silent=True) or {}

    # Quick validation for required fields
    required = ["universeId", "notificationId", "key", "time", "message", "api_key"] 
    for field in required:
        if field not in receivedData:
            return {"error": f"Missing field: {field}"}, 400

    # Now pass to your deeper validation
    errorMessage, statusCode = utility.validData(receivedData)
    if statusCode != 200:
        return errorMessage, statusCode

    utility.writeToFile(receivedData["universeId"], str(receivedData["key"]), receivedData)

    return "", 200 

@app.route("/", methods=["GET"])
def index():
    print("[GET] request")
    return "Hello World!"
