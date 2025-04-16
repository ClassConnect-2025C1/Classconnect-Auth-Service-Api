import requests
from fastapi import HTTPException
NOTIFICATION_SERVICE_URL = "http://localhost:8001/notifications"

def send_notification(to: str, pin: str, channel: str):
    payload = {
        "to": to,
        "pin": pin,
        "channel": channel
    }
    try:
        response = requests.post(NOTIFICATION_SERVICE_URL, json=payload)

        if response.status_code == 200:
            return True
        elif response.status_code == 502:
            raise HTTPException(status_code=502, detail="Notification rejected by provider")
        elif response.status_code == 403:
            raise HTTPException(status_code=403, detail="Notification forbidden")
        else:
            raise HTTPException(status_code=500, detail="Unexpected error from notification service")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")