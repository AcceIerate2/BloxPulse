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
from scheduler import loop_scheduler

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


def _start_scheduler_once():
    # avoid double-start when reloader or multiple workers are present
    if os.environ.get("_SCHEDULER_STARTED") == "1":
        return
    os.environ["_SCHEDULER_STARTED"] = "1"
    t = threading.Thread(target=loop_scheduler, daemon=True)
    t.start()
    print("[scheduler] started", flush=True)

# Start only if we want it running in this dyno
if os.getenv("RUN_SCHEDULER") == "1":
    _start_scheduler_once()