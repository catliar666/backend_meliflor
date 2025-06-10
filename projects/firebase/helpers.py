from .auth import obtener_token_acceso
import requests
import os

import re

def validar_horario_string(horario):
    pattern = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')
    if not pattern.match(horario.strip()):
        raise ValueError("El horarioAdministracion debe estar en formato HH:MM (ej. 08:30)")
    return horario.strip()

from datetime import datetime, timezone, timedelta

# Conversión de timestamp ISO Firestore a UTC+2 en formato string legible
def convertir_fecha_utc_a_local(timestamp_str, offset_horas=2):
    if not timestamp_str:
        return ""
    dt_utc = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    zona_local = timezone(timedelta(hours=offset_horas))
    dt_local = dt_utc.astimezone(zona_local)
    return dt_local.strftime("%Y-%m-%d %H:%M:%S")  # o usa el formato que prefieras


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
    firestore_fields = {}

    campos_timestamp = {
        "fecha", "fechaRecordatorio", "fechaDiagnostico", "fechaNotificacion",
        "fechaFin", "fechaComienzo", "fechaInscripcion", "cumpleanios"
    }

    campos_referencia = {
        "alumno", "ausencias", "conflictos", "consumo", "enfermedades", "alergias",
        "medicamentos", "necesidades", "rutinaSuenio", "idPlato", "platos",
        "idUser", "hijos"
    }

    project_id = os.getenv("PROJECT_ID")

    for key, value in data.items():
        # Timestamps
        if key in campos_timestamp:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                dt = value
            utc_dt = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            firestore_fields[key] = {"timestampValue": utc_dt}

        # Referencias (individuales o listas)
        elif key in campos_referencia:
            if isinstance(value, list):
                # Manejar lista de referencias
                references = []
                for item in value:
                    path = item.lstrip("/") if isinstance(item, str) else str(item)
                    reference = f"projects/{project_id}/databases/(default)/documents/{path}"
                    references.append({"referenceValue": reference})
                firestore_fields[key] = {"arrayValue": {"values": references}}
            else:
                # Manejar referencia individual
                path = value.lstrip("/") if isinstance(value, str) else str(value)
                reference = f"projects/{project_id}/databases/(default)/documents/{path}"
                firestore_fields[key] = {"referenceValue": reference}

        # Strings
        elif isinstance(value, str):
            firestore_fields[key] = {"stringValue": value}

        # Booleanos
        elif isinstance(value, bool):
            firestore_fields[key] = {"booleanValue": value}

        # Enteros
        elif isinstance(value, int):
            firestore_fields[key] = {"integerValue": str(value)}

        # Lista de DateTime (cuotaPagada, etc.)
        elif isinstance(value, list) and all(isinstance(v, (datetime, str)) for v in value):
            try:
                timestamp_values = []
                for v in value:
                    if isinstance(v, str):
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    else:
                        dt = v
                    utc_dt = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                    timestamp_values.append({"timestampValue": utc_dt})

                firestore_fields[key] = {"arrayValue": {"values": timestamp_values}}
            except Exception:
                firestore_fields[key] = {
                    "arrayValue": {"values": [{"stringValue": str(v)} for v in value]}
                }

        # Lista de strings normales (no referencias ni timestamps)
        elif isinstance(value, list):
            firestore_fields[key] = {
                "arrayValue": {"values": [{"stringValue": str(v)} for v in value]}
            }

        else:
            raise ValueError(f"No se puede procesar el campo '{key}' con valor '{value}'")

    return {"fields": firestore_fields}




