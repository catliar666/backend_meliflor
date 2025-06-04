from .auth import obtener_token_acceso
from .parsers.usuarios_parse import parse_usuario_document
from .parsers.alumnos_parse import parse_alumno_document
from .parsers.administradores_parse import parse_administrador_document
from .parsers.noticias_parse import parse_noticia_document
from .parsers.notificaciones_parse import parse_notificacion_document
from .parsers.medicamentos_parse import parse_medicamento_document
from .parsers.menus_parse import parse_menu_document
from .helpers import transformar_a_firestore_fields, validar_horario_string
from datetime import datetime, timedelta

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()



def get_usuario_completo(request, uid):
    token = obtener_token_acceso()
    url = f"{os.getenv('URL_USUARIO')}{uid}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    if request.method == "GET":
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {"code": "500", "error": f"{response.status_code}: {response.text}"}

        doc = response.json()
        usuario = parse_usuario_document(doc)
        return {"code": "200", "message": usuario}

    elif request.method == "PATCH":
        try:
            headers["Content-Type"] = "application/json"
            data = json.loads(request.body)
            datos_transformados = transformar_a_firestore_fields(data)

            response = requests.patch(url, headers=headers, json=datos_transformados)

            if response.status_code not in [200, 201]:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return {"code": "200", "message": "Usuario modificado correctamente", "uid": uid}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            headers["Content-Type"] = "application/json"
            data = json.loads(request.body)

            # Campos obligatorios
            campos_obligatorios = [
                "nombre", "apellidos", "dni", "telefono", "telefonoEmergencia",
                "direccion", "genero", "ocupacion", "nacionalidad", "estadoCivil",
                "fechaInscripcion", "role", "suscripcion", "autorizacionFotos",
                "autorizacionExcursiones", "custodia", "seguroMedico"
            ]

            campos_faltantes = [campo for campo in campos_obligatorios if campo not in data]
            if campos_faltantes:
                return {
                    "code": "400",
                    "error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"
                }

            datos_transformados = transformar_a_firestore_fields(data)

            response = requests.patch(url, headers=headers, json=datos_transformados)

            if response.status_code not in [200, 201]:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return {"code": "201", "message": "Usuario creado/modificado correctamente", "uid": uid}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}



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

    return {"code":"200", "message": administrador}




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
        return {"code":"200", "message": menus}

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

            return {"code":"200", "message": notas}

        except Exception as e:
            return {"code": "500", "error": str(e)}



def get_alumnos(request):
    token = obtener_token_acceso()
    base_url = f"{os.getenv('URL_INICIO')}{os.getenv('URL_ALUMNOS')}"
    uid = request.GET.get("uid")
    nombre = request.GET.get("nombre")
    apellidos = request.GET.get("apellidos")
    cumpleanios = request.GET.get("cumpleanios")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                url = f"{base_url}{uid}"
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return {"code": "404", "error": f"No se encontró el alumno con UID {uid}"}
                data = response.json()
                alumno = parse_alumno_document(data)
                return {"code": "200", "message": alumno}

            elif nombre or apellidos or cumpleanios:
                filtros = []
                if nombre:
                    filtros.append({
                        "fieldFilter": {
                            "field": {"fieldPath": "nombre"},
                            "op": "EQUAL",
                            "value": {"stringValue": nombre}
                        }
                    })
                elif apellidos:
                    filtros.append({
                        "fieldFilter": {
                            "field": {"fieldPath": "apellidos"},
                            "op": "EQUAL",
                            "value": {"stringValue": apellidos}
                        }
                    })
                elif cumpleanios:
                    filtros.append({
                        "fieldFilter": {
                            "field": {"fieldPath": "cumpleanios"},
                            "op": "EQUAL",
                            "value": {"timestampValue": cumpleanios}
                        }
                    })

                body = {
                    "structuredQuery": {
                        "from": [{"collectionId": "alumnos"}],
                        "where": filtros[0]
                    }
                }

                query_url = os.getenv('URL_INDICE')
                response = requests.post(query_url, headers=headers, json=body)

                if response.status_code != 200:
                    return {"code": "500", "error": f"Error en runQuery: {response.text}"}

                query_results = response.json()
                alumnos = [
                    parse_alumno_document(result["document"])
                    for result in query_results if "document" in result
                ]

                return {"code": "200", "message": alumnos}

            else:
                # Obtener todos los alumnos
                response = requests.get(base_url, headers=headers)
                if response.status_code != 200:
                    return {"code": "500", "error": response.text}
                data = response.json()
                documentos = data.get("documents", [])
                alumnos = [parse_alumno_document(doc) for doc in documentos]
                return {"code": "200", "message": alumnos}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            campos_obligatorios = ["nombre", "apellidos", "genero", "edad", "idioma", "cumpleanios"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {
                    "code": "400",
                    "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"
                }

            firestore_payload = {
                "fields": {
                    "nombre": {"stringValue": data["nombre"]},
                    "apellidos": {"stringValue": data["apellidos"]},
                    "genero": {"stringValue": data["genero"]},
                    "edad": {"integerValue": str(data["edad"])},
                    "idioma": {"stringValue": data["idioma"]},
                    "cumpleanios": {"timestampValue": data["cumpleanios"]}
                }
            }

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {
                    "code": str(response.status_code),
                    "error": f"Firestore error: {response.text}"
                }

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Alumno añadido correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            data = json.loads(request.body)
            uid = request.GET.get("uid")

            if not uid:
                return {"code": "400", "error": "Falta el campo obligatorio 'uid' para identificar el alumno"}
            campos_actualizados = {}
            for key, value in data.items():
                if key == "uid":
                    continue
                if key == "edad":
                    campos_actualizados[key] = {"integerValue": str(value)}
                elif key == "cumpleanios":
                    campos_actualizados[key] = {"timestampValue": value}
                else:
                    campos_actualizados[key] = {"stringValue": value}

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            url_patch = f"{base_url}{uid}"
            payload = {"fields": campos_actualizados}

            response = requests.patch(url_patch, headers=headers, json=payload)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Alumno '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


    

def get_noticias(request):
    token = obtener_token_acceso()
    base_url = os.getenv("URL_NOTICIAS")
    query_url = os.getenv("URL_INDICE")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    uid = request.GET.get("uid")
    fecha = request.GET.get("fecha")
    fecha_iso = None

    if fecha:
        try:
            fecha_iso = datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            return {"code": "400", "error": "Formato de fecha inválido. Usa DD/MM/YYYY"}

    if request.method == "GET":
        try:
            if fecha_iso:
                end_date = fecha_iso + timedelta(days=1)
                query = {
                    "structuredQuery": {
                        "from": [{"collectionId": "noticias"}],
                        "where": {
                            "compositeFilter": {
                                "op": "AND",
                                "filters": [
                                    {
                                        "fieldFilter": {
                                            "field": {"fieldPath": "fecha"},
                                            "op": "GREATER_THAN_OR_EQUAL",
                                            "value": {"timestampValue": fecha_iso.isoformat() + "Z"}
                                        }
                                    },
                                    {
                                        "fieldFilter": {
                                            "field": {"fieldPath": "fecha"},
                                            "op": "LESS_THAN",
                                            "value": {"timestampValue": end_date.isoformat() + "Z"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }

                response = requests.post(query_url, headers=headers, json=query)

                if response.status_code != 200:
                    return {"code": "500", "error": f"Error en búsqueda por fecha: {response.text}"}

                resultados = response.json()
                noticias = [parse_noticia_document(r["document"]) for r in resultados if "document" in r]

                return {"code": "200", "message": noticias}

            else:
                # Si no se pidió fecha, se traen todas las noticias
                response = requests.get(base_url, headers=headers)

                if response.status_code != 200:
                    return {"code": "500", "error": response.text}

                data = response.json()
                documentos = data.get("documents", [])
                noticias = [parse_noticia_document(doc) for doc in documentos]

                return {"code": "200", "message": noticias}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            campos_obligatorios = ["titulo", "descripcion", "imagen"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}

            firestore_payload = {
                "fields": {
                    "titulo": {"stringValue": data["titulo"]},
                    "descripcion": {"stringValue": data["descripcion"]},
                    "foto": {"stringValue": data["imagen"]},
                    "fecha": {"timestampValue": datetime.utcnow().isoformat() + "Z"}
                }
            }

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "201", "message": "Noticia añadida correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "UID requerido para actualizar la noticia"}

            data = json.loads(request.body)
            campos_actualizados = {}

            for k, v in data.items():
                if k == "fecha":
                    campos_actualizados[k] = {"timestampValue": v}
                elif k == "foto":
                    campos_actualizados["foto"] = {"stringValue": v}
                else:
                    campos_actualizados[k] = {"stringValue": v}

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            url_patch = f"{base_url}{uid}"
            payload = {"fields": campos_actualizados}

            response = requests.patch(url_patch, headers=headers, json=payload)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Noticia '{uid}' actualizada correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


    

def enviar_notificacion(request):
    access_token = obtener_token_acceso()
    uid = request.GET.get("uid")

    if request.method == "GET":
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        if uid:
                firestore_url = os.getenv("URL_INDICE")
                user_ref = f"{os.getenv('REFERENCIA_USER')}{uid}"

                body = {
                    "structuredQuery": {
                        "from": [{"collectionId": "notificaciones"}],
                        "where": {
                            "fieldFilter": {
                                "field": {"fieldPath": "idUser"},
                                "op": "EQUAL",
                                "value": {"referenceValue": user_ref}
                            }
                        }
                    }
                }

                response = requests.post(firestore_url, headers=headers, json=body)

                if response.status_code != 200:
                    return {"code": "500", "error": f"Firestore query error: {response.text}"}

                try:
                    data = response.json()
                    documentos = [item["document"] for item in data if "document" in item]

                    notificaciones = [
                        parse_notificacion_document(doc) for doc in documentos
                    ]

                    return {"code": "200", "message": notificaciones}

                except Exception as e:
                    import traceback
                    print("[ERROR] Excepción al parsear documentos con filtro:")
                    traceback.print_exc()
                    return {"code": "500", "error": str(e)}

        else:
                url = os.getenv("URL_NOTIFICACIONES")
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return {"code": "500", "error": response.text}

                try:
                    data = response.json()
                    documentos = data.get("documents", [])

                    notificaciones = [
                        parse_notificacion_document(doc) for doc in documentos
                    ]

                    return {"code": "200", "message": notificaciones}

                except Exception as e:
                    import traceback
                    print("[ERROR] Excepción al procesar notificaciones sin filtro:")
                    traceback.print_exc()
                    return {"code": "500", "error": str(e)}



    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            fcm_token = data.get("fcm_token")
            titulo = data.get("titulo")
            cuerpo = data.get("cuerpo")
            usuario_id = data.get("idUser")
            ruta = data.get("ruta")

            if not all([fcm_token, titulo, cuerpo, usuario_id]):
                return {"code": "400", "error": "Campos requeridos faltantes"}

            headers = {
                "Content-Type": "application/json",
                "Authorization": f'Bearer {access_token}'
            }

            payload = {
                "message": {
                    "token": fcm_token,
                    "notification": {
                        "title": titulo,
                        "body": cuerpo
                    },
                    "data": {
                        "route": ruta
                    }
                }
            }

            response = requests.post(
                os.getenv('URL_MESSAGE_SEND'),
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code not in [200, 202]:
                return {
                    "code": response.status_code,
                    "error": f"FCM error {response.status_code}: {response.text}"
                }

            # 🗃️ Guardar en Firestore
            firestore_payload = {
                "fields": {
                    "idUser": {"referenceValue": f"{os.getenv('REFERENCIA_USER')}{usuario_id}"},
                    "titulo": {"stringValue": titulo},
                    "cuerpo": {"stringValue": cuerpo},
                    "fecha": {"timestampValue": datetime.utcnow().isoformat() + "Z"},
                    "leido": {"booleanValue": False},
                    "ruta": {"stringValue": ruta},
                }
            }

            firestore_response = requests.post(
                os.getenv('URL_NOTIFICACIONES'),
                headers=headers,
                data=json.dumps(firestore_payload)
            )

            if firestore_response.status_code != 200:
                return {
                    "code": firestore_response.status_code,
                    "error": f"Firestore error: {firestore_response.text}"
                }

            return {"code": "200", "message": "Notificación enviada y guardada correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


def get_medicamentos(request, uid):
    token = obtener_token_acceso()
    base_url = f'{os.getenv("URL_MEDICAMENTOS")}{uid}'
    query_url = os.getenv("URL_INDICE")

    if request.method == "GET":
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()
            medicamento = parse_medicamento_document(data)

            return {"code": "200", "message": medicamento}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            campos_obligatorios = ["nombre", "dosis", "horarioAdministracion", "frecuencia", "metodoAdministracion"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}

            try:
                horario_valido = validar_horario_string(data["horarioAdministracion"])
            except ValueError as e:
                return {"code": "400", "error": str(e)}

            firestore_payload = {
                "fields": {
                    "nombre": {"stringValue": data["nombre"]},
                    "dosis": {"stringValue": data["dosis"]},
                    "horarioAdministracion": {"stringValue": horario_valido}
                }
            }

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {
                "code": "201",
                "message": "Medicamento añadido correctamente",
                "id": document_id
            }


        except Exception as e:
            return {"code": "500", "error": str(e)} 




    




