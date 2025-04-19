import requests
from fastapi import HTTPException
import os

prefix = os.getenv('URL_NOTIFICATION')
NOTIFICATION_SERVICE_URL = prefix +"/notifications"

def send_notification(to: str, pin: str, channel: str):
    payload = {
        "to": to,
        "body": pin,
        "channel": channel
    }
    print(f"Sending notification to {to} via {channel} with body: {pin}")
    try:
        response = requests.post(NOTIFICATION_SERVICE_URL, json=payload)
        print(f"Notification service response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Notification rejected by provider")
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="One or more fields are missing or invalid")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")