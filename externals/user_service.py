import requests
from fastapi import HTTPException
import os

prefix = os.getenv('URL_USERS')

def get_user_data(id: str):
    USER_SERVICE_URL = prefix + "/users/profile/" + id
    #print(f"Getting user {id} data")
    try:
        response = requests.get(USER_SERVICE_URL)
        #print(f"User service response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="One or more fields are missing or invalid")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")

def update_user_data(id: str, data: dict):
    USER_SERVICE_URL = prefix + "/users/profile/" + id
    #print(f"Updating user {id} data with {data}")
    try:
        response = requests.patch(USER_SERVICE_URL, json=data)
        #print(f"User service response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="One or more fields are missing or invalid")
        elif response.status_code == 422:
            raise HTTPException(status_code=403, detail="User not authorized to update this data")

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Notification service unavailable: {str(e)}")
