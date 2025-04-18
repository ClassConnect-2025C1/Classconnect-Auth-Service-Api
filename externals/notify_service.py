import requests
from fastapi import HTTPException
NOTIFICATION_SERVICE_URL = "http://localhost:8003/notifications"

def send_notification(to: str, pin: str, channel: str):
    payload = {
        "to": to,
        "body": pin,
        "channel": channel
    }
    try:
        response = requests.post(NOTIFICATION_SERVICE_URL, json=payload)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Notification rejected by provider")
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="Notification forbidden")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")