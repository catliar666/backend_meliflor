from .auth import obtener_token_acceso
import requests

import re

def validar_horario_string(horario):
    pattern = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')
    if not pattern.match(horario.strip()):
        raise ValueError("El horarioAdministracion debe estar en formato HH:MM (ej. 08:30)")
    return horario.strip()

def fetch_document_by_reference(ref_url):
    token = obtener_token_acceso()
    url = f"https://firestore.googleapis.com/v1/{ref_url}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener {ref_url}: {response.status_code} - {response.text}")
    
def transformar_a_firestore_fields(data: dict) -> dict:

    from datetime import datetime

    firestore_fields = {}

    for key, value in data.items():
        if isinstance(value, datetime) or (isinstance(value, str) and "T" in value):
            firestore_fields[key] = {
                "timestampValue": value if isinstance(value, str) else value.isoformat() + "Z"
            }

        # Integer
        elif isinstance(value, int):
            firestore_fields[key] = {"integerValue": str(value)}

        # Float
        elif isinstance(value, float):
            firestore_fields[key] = {"doubleValue": value}

        # Boolean
        elif isinstance(value, bool):
            firestore_fields[key] = {"booleanValue": value}


        elif isinstance(value, str) and value.startswith("projects/"):
            firestore_fields[key] = {"referenceValue": value}

        # Lista de referencias
        elif isinstance(value, list) and all(isinstance(v, str) and v.startswith("projects/") for v in value):
            firestore_fields[key] = {
                "arrayValue": {
                    "values": [{"referenceValue": v} for v in value]
                }
            }

        # Lista de strings
        elif isinstance(value, list) and all(isinstance(v, str) for v in value):
            firestore_fields[key] = {
                "arrayValue": {
                    "values": [{"stringValue": v} for v in value]
                }
            }

        # String normal
        elif isinstance(value, str):
            firestore_fields[key] = {"stringValue": value}

        else:
            raise ValueError(f"No se puede procesar el campo '{key}' con valor '{value}'")

    return {"fields": firestore_fields}
