import requests
from fastapi import HTTPException
import os

prefix = os.getenv('URL_NOTIFICATION')
NOTIFICATION_SERVICE_URL = prefix +"/notifications"

text_recovery_template = (
    "Recibiste este correo porque se solicitó un cambio de contraseña para tu cuenta.\n\n"
    "Si fuiste vos, utiliza este PIN para reestablecerla:\n{}\n\n"
    "Si no fuiste vos, podés ignorar este mensaje. Tu contraseña no se cambiará."
)
html_recovery_template = (
    '<p>Recibiste este correo porque se solicitó un cambio de contraseña para tu cuenta.</p>\n'
    '<p>Si fuiste vos, utiliza este PIN para reestablecerla:</p>\n'
    '<p style="font-weight: bold; color: #1a73e8;">{}</p>\n'
    '<p>Si no fuiste vos, podés ignorar este mensaje. Tu contraseña no se cambiará.</p>'
)

def send_notification(to: str, pin: str, channel: str):
    payload = {
        "To": to,
        "Body": pin,
        "Channel": channel
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
    

def send_email_recovery(to_email: str, body: str):
    email_service_url = prefix + "/notifications/email"
    payload = {
        "receiver_email": to_email,
        "subject": "ClassConnect Password Recovery",
        "text": text_recovery_template.format(body),
        "html": html_recovery_template.format(body)
    }
    print(f"Sending email to {to_email} with body: {body}")
    try:
        response = requests.post(email_service_url, json=payload)
        print(f"Notification service response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Email rejected by provider")
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="One or more fields are missing or invalid")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")