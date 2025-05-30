from google.oauth2 import service_account
from google.auth.transport.requests import Request 
import json
import os

def obtener_token_acceso():
    SCOPES = ["https://www.googleapis.com/auth/datastore"]

    # Lee el JSON desde la variable de entorno y lo convierte en dict
    firebase_config_json = os.getenv('FIREBASE_CONFIG')
    if not firebase_config_json:
        raise Exception("FIREBASE_CONFIG no está definida en las variables de entorno")

    cred_dict = json.loads(firebase_config_json)

    # Crea las credenciales directamente desde el dict
    credentials = service_account.Credentials.from_service_account_info(
        cred_dict, scopes=SCOPES
    )

    credentials.refresh(Request())
    return credentials.token


