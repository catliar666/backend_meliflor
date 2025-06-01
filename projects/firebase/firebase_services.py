from .auth import obtener_token_acceso
from .parsers.usuarios_parse import parse_usuario_document
from .parsers.alumnos_parse import parse_alumno_document
from .parsers.administradores_parse import parse_administrador_document
from .parsers.menus_parse import parse_menu_document
from .helpers import fetch_document_by_reference, transformar_a_firestore_fields
from datetime import datetime, timedelta

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


def get_usuario_completo(request, uid):
    token = obtener_token_acceso()
    url = f"{os.getenv('URL_USUARIO')}{uid}"
    if request.method == "GET":


        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            Exception(f"Error {response.status_code}: {response.text}")
            return None

        doc = response.json()
        usuario = parse_usuario_document(doc)

        hijos_refs = usuario.get("hijos", [])
        hijos_completos = []

        for ref in hijos_refs:
            alumno_doc = fetch_document_by_reference(ref)
            hijo = parse_alumno_document(alumno_doc)
            hijos_completos.append(hijo)

        usuario["hijos"] = hijos_completos
        return usuario
    
    else:
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":"application/json"
        }
        datos_transformados = transformar_a_firestore_fields(json.loads(request.body))
        response = requests.patch(url, headers=headers, json=datos_transformados)

        if response.status_code not in [200, 201]:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return {"message": "Usuario creado correctamente", "uid": uid}

def get_administradores_completo(uid):
    token = obtener_token_acceso()
    url = f"{os.getenv('URL_ADMINISTRADORES')}{uid}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        Exception(f"Error {response.status_code}: {response.text}")
        return None

    doc = response.json()
    administrador = parse_administrador_document(doc)

    return administrador




def obtener_rango_semana_actual():
    hoy = datetime.utcnow()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return (
        inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0).isoformat("T") + "Z",
        fin_semana.replace(hour=23, minute=59, second=59, microsecond=999000).isoformat("T") + "Z",
    )


def obtener_menu_de_la_semana(request):
    token = obtener_token_acceso()

    if request.method == "GET":
        url = os.getenv('URL_INDICE')
        fecha_inicio, fecha_fin = obtener_rango_semana_actual()

        query = {
            "structuredQuery": {
                "from": [{"collectionId": "menus"}],
                "where": {
                    "compositeFilter": {
                        "op": "AND",
                        "filters": [
                            {
                                "fieldFilter": {
                                    "field": {"fieldPath": "fechaComienzo"},
                                    "op": "GREATER_THAN_OR_EQUAL",
                                    "value": {"timestampValue": fecha_inicio}
                                }
                            },
                            {
                                "fieldFilter": {
                                    "field": {"fieldPath": "fechaFin"},
                                    "op": "LESS_THAN_OR_EQUAL",
                                    "value": {"timestampValue": fecha_fin}
                                }
                            }
                        ]
                    }
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=query)

        if response.status_code != 200:
            return {"code":f"{response.status_code}","message": f"{response.text}"}

        resultados = response.json()
        menus = [parse_menu_document(item["document"]) for item in resultados if "document" in item]
        return menus

    elif request.method == "POST":
        try:
            url = os.getenv('URL_MENUS')
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            datos_transformados = transformar_a_firestore_fields(json.loads(request.body))
            response = requests.post(url, headers=headers, json=datos_transformados)

            if response.status_code != 200:
                return {"code":f"{response.status_code}","message": f"{response.text}"}

            return {"code":"200","message": "Menú creado correctamente"}

        except Exception as e:
            raise Exception(str(e))

    raise Exception("Método no permitido")

def get_notas_alumno(request, uid):
    token = obtener_token_acceso()
    url = f"{os.getenv('URL_ALUMNOS')}{uid}"

    if request.method == "GET":
        try:
            query = {
            "structuredQuery": {
                "from": [{"collectionId": "notas"}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "alumno"},
                        "op": "EQUAL",
                        "value": {
                            "referenceValue": url
                        }
                    }
                }
            }
        }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            urlIndice = os.getenv('URL_INDICE')
            response = requests.post(urlIndice, headers=headers, json=query)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            notas_raw = response.json()
            notas = [
                {
                    "descripcion": n["document"]["fields"]["descripcion"]["stringValue"],
                    "fecha": n["document"]["fields"]["fecha"]["timestampValue"],
                    "id": n["document"]["name"].split("/")[-1]
                }
                for n in notas_raw if "document" in n
            ]

            return notas

        except Exception as e:
            return {"code": "500", "error": str(e)}


def get_alumnos(request):
    token = obtener_token_acceso()
    url = f'https://firestore.googleapis.com/v1/{os.getenv("URL_ALUMNOS")}'
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"code": "500", "error": response.text}

    try:
        data = response.json()
        documentos = data.get("documents", [])

        alumnos = [
            parse_alumno_document(doc) for doc in documentos
        ]

        return alumnos

    except Exception as e:
        return {"code": "500", "error": str(e)}


    




