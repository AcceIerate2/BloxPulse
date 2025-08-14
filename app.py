from flask import Flask, request
import requests
from src import utility
from filelock import FileLock
import json
import time
import threading

from typing import TypedDict
class ReceivedData(TypedDict):
    universeId: str # straight forward
    notificationId: str # assetid for notifications
    key: str # userid
    time: int # set the exact time (that unix epoch thingy)
    message: str # messsage to send

dataFilePath = "data.json"

app = Flask(__name__)

def loop_scheduler():
    while True:
        lock = FileLock(f"{dataFilePath}.lock")
        with lock:
            with open(dataFilePath, "r") as f:
                fileContent = json.load(f)

            now = time.time()

            for refId, entry in list(fileContent.items()):
                if now >= entry.get("time", 0):
                    print(f"Push to {refId}: {entry['message']}")
                    del fileContent[refId]  # remove after sending

            with open(dataFilePath, "w") as f:
                json.dump(fileContent, f, indent=4)

        time.sleep(1)  # wait 1 second before checking again

@app.route("/Schedule", methods=["POST"])
def Schedule():
    receivedData: ReceivedData = request.get_json() 

    errorMesssage, statusCode = utility.validData(receivedData)
    if type(statusCode) == int and statusCode != 200:
        return errorMesssage, statusCode

    utility.writeToFile(receivedData["universeId"], str(receivedData["key"]), receivedData)

    return 200    

@app.route("/")
def index():
    return 200

if __name__ == "__main__":
    threading.Thread(target=loop_scheduler).start()
    app.run()