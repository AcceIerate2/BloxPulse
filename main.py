from flask import Flask, request, jsonify
import requests
from src import utility
from filelock import FileLock
import json
import time
import threading
from src import notificationHandler
import os
import warnings

from typing import TypedDict
class ReceivedData(TypedDict):
    universeId: str # straight forward
    notificationId: str # assetid for notifications
    key: str # userid
    time: int # set the exact time (that unix epoch thingy)
    message: str # messsage to send
    api_key: str

app = Flask(__name__)
from src.utility import dataFilePath, lock

def loop_scheduler():
    while True: 
        with lock:
            with open(f"{dataFilePath}", "r", encoding="utf-8") as f:
                fileContent = json.load(f)

        keysToRemove = {}
        currentTime = int(time.time())

        for universeId in fileContent:
            for key in fileContent[universeId]:
                notificationData: ReceivedData = fileContent[universeId][key]

                deadline = notificationData["time"]
                if currentTime >= deadline:
                    try:
                        notificationHandler.pushNotification(notificationData)
                        print("Push")
                    except Exception as e:
                        warnings.warn(f"Notification failed: {e}", RuntimeWarning)

                    keysToRemove[key] = universeId

        with lock:
            with open(f"{dataFilePath}", "r", encoding="utf-8") as f:
                fileContent = json.load(f)

            for keyToBeRemoved, keyUniverseId in keysToRemove.items():
                if keyUniverseId in fileContent and keyToBeRemoved in fileContent[keyUniverseId]:
                    del fileContent[keyUniverseId][keyToBeRemoved]

            with open(f"{dataFilePath}", "w", encoding="utf-8") as f:
                json.dump(fileContent, f, indent=2, ensure_ascii=False)

        time.sleep(2)

threading.Thread(target=loop_scheduler, daemon=True).start()

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

@app.route("/data", methods=["GET"])
def data():
    with lock:
        with open(f"{dataFilePath}", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
        
    return "Couldn't get data."

@app.route("/", methods=["GET"])
def index():
    print("[GET] request")
    return "Hello World!"
