from .auth import obtener_token_acceso
from .parsers.usuarios_parse import parse_usuario_document
from .parsers.alumnos_parse import parse_alumno_document
from .parsers.administradores_parse import parse_administrador_document
from .parsers.noticias_parse import parse_noticia_document
from .parsers.notificaciones_parse import parse_notificacion_document
from .parsers.medicamentos_parse import parse_medicamento_document
from .parsers.alergias_parse import parse_alergias_document
from .parsers.menus_parse import parse_menu_document
from.parsers.enfermedades_parse import parse_enfermedad_document
from .parsers.necesidades_parse import parse_necesidad_document
from.parsers.conflictos_parse import parse_conflicto_document
from .parsers.suenio_parse import parse_suenio_document
from .parsers.mochilas_parse import parse_mochila_document
from .parsers.ausencias_parse import parse_ausencia_document
from .parsers.consumo_parse import parse_consumo_document
from .parsers.notas_parse import parse_notas_document
from .helpers import transformar_a_firestore_fields, validar_horario_string
from datetime import datetime, timedelta

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()



def get_usuario_completo(request):
    token = obtener_token_acceso()
    uid = request.GET.get("uid")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if not uid:
                # Obtener todos los usuarios (solo id, nombre y apellidos)
                url = os.getenv('URL_USUARIO')
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    return {"code": "500", "error": f"Error al obtener usuarios: {response.status_code}: {response.text}"}
                print(response.text)
                try:
                    usuarios_data = response.json()
                    if "documents" not in usuarios_data:
                        return {
                            "code": "500",
                            "error": "Formato de respuesta inesperado",
                            "response_sample": str(data)[:200]
                        }
                    usuarios = []
                    for doc in usuarios_data["documents"]:
                        doc_id = doc["name"].split("/")[-1]
                        fields = doc.get("fields", {})
                        
                        usuarios.append({
                            "id": doc_id,
                            "nombre": fields.get("nombre", {}).get("stringValue", ""),
                            "apellidos": fields.get("apellidos", {}).get("stringValue", "")
                        })
                    
                    return {"code": "200", "message": usuarios}
                except ValueError:
                    return {"code": "500", "error": "La respuesta no es un JSON válido"}
            else:
                # Obtener usuario específico
                url = f"{os.getenv('URL_USUARIO')}{uid}"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return {"code": "500", "error": f"Error al obtener usuario: {response.status_code}: {response.text}"}

                try:
                    doc = response.json()
                    usuario = parse_usuario_document(doc)
                    return {"code": "200", "message": usuario}
                except ValueError:
                    return {"code": "500", "error": "La respuesta del usuario no es un JSON válido"}
                
        except Exception as e:
            return {"code": "500", "error": f"Error inesperado: {str(e)}"}


    elif request.method == "PATCH":
        try:
            headers["Content-Type"] = "application/json"
            data = json.loads(request.body)

            uid = request.GET.get("uid")
            if not uid:
                return {
                    "code": "400",
                    "error": "Falta el parámetro 'uid' en la URL"
                }

            campos_permitidos = {
                "nombre", "apellidos", "dni", "telefono", "telefonoEmergencia",
                "direccion", "genero", "ocupacion", "nacionalidad", "estadoCivil",
                "fechaInscripcion", "role", "suscripcion", "autorizacionFotos",
                "autorizacionExcursiones", "custodia", "seguroMedico",
                "cuotaPagada", "hijos", "tokenFCM"
            }

            campos_recibidos = set(data.keys())
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }

            datos_transformados = transformar_a_firestore_fields(data)

            # Construye la URL del documento con el UID
            update_mask = "&".join([f"updateMask.fieldPaths={campo}" for campo in data.keys()])
            url = f"{os.getenv('URL_USUARIO')}{uid}?{update_mask}"


            print("📤 PATCH a Firestore")
            print("➡️ URL:", url)
            print("➡️ Headers:", headers)
            print("➡️ Body enviado:", datos_transformados)

            response = requests.patch(url, headers=headers, json=datos_transformados)

            print("⬅️ Status code:", response.status_code)
            print("⬅️ Respuesta:", response.text)

            if response.status_code not in [200, 201]:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return {
                "code": "200",
                "message": "Usuario modificado correctamente",
                "uid": uid
            }

        except Exception as e:
            print("❌ Excepción durante PATCH:")
            print("🧾 Request body original:", request.body)
            print("📦 Headers:", headers)
            print("📍 UID:", uid)
            print("🔧 Traceback:\n", traceback.format_exc())

            return {"code": "500", "error": str(e)}


    elif request.method == "POST":
        try:
            headers["Content-Type"] = "application/json"
            data = json.loads(request.body)
            project_id = os.getenv('PROJECT_ID')

            id_usuario = data.get("id")
            if not id_usuario:
                return {"code": "400", "error": "Falta el campo 'id' en el cuerpo de la solicitud"}

            campos_obligatorios = [
                "nombre", "apellidos", "dni", "telefono", "telefonoEmergencia",
                "direccion", "genero", "ocupacion", "nacionalidad", "estadoCivil",
                "fechaInscripcion", "role", "autorizacionFotos",
                "autorizacionExcursiones", "custodia", "seguroMedico", "cuotaPagada"
            ]

            campos_faltantes = [campo for campo in campos_obligatorios if campo not in data]
            if campos_faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"}

            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios + ["hijos", "id"])  # Añadir "id" a los campos permitidos
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {"code": "400", "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"}

            # Eliminar el campo 'id' del data para que no se incluya en los fields
            data_sin_id = {k: v for k, v in data.items() if k != "id"}
            datos_transformados = transformar_a_firestore_fields(data_sin_id)

            # URL para crear un documento con ID específico
            urlPost = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/usuarios?documentId={id_usuario}"
            
            # Usamos POST para crear un nuevo documento
            response = requests.post(
                urlPost, 
                headers=headers, 
                json={"fields": datos_transformados["fields"]}
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return {"code": "201", "message": "Usuario creado correctamente", "uid": id_usuario}

        except Exception as e:
            return {"code": "500", "error": str(e)}


    return {"code": "405", "error": "Método no permitido"}



def get_administradores_completo(request):
    token = obtener_token_acceso()
    uid = request.GET.get("uid")
    url = f"{os.getenv('URL_ADMINISTRADORES')}{uid}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        Exception(f"Error {response.status_code}: {response.text}")
        return {"code":"404", "message":"Usuario no encontrado"}

    doc = response.json()
    administrador = parse_administrador_document(doc)

    return {"code":"200", "message": administrador}




from datetime import datetime, timedelta, timezone

def obtener_rango_semana_actual():
    utc_plus_2 = timezone(timedelta(hours=2))
    hoy = datetime.now(utc_plus_2)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return (
        inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat("T").replace("+00:00", "Z"),
        fin_semana.replace(hour=23, minute=59, second=59, microsecond=999000).astimezone(timezone.utc).isoformat("T").replace("+00:00", "Z"),
    )


import traceback
def obtener_menu_de_la_semana(request):
    token = obtener_token_acceso()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

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



        response = requests.post(url, headers=headers, json=query)

        if response.status_code != 200:
            return {"code":f"{response.status_code}","message": f"{response.text}"}

        resultados = response.json()
        menus = [parse_menu_document(item["document"]) for item in resultados if "document" in item]
        return {"code":"200", "message": menus}

    elif request.method == "POST":
        try:
            url = os.getenv('URL_MENUS')

            datos_transformados = transformar_a_firestore_fields(json.loads(request.body))
            response = requests.post(url, headers=headers, json=datos_transformados)

            if response.status_code != 200:
                return {"code":f"{response.status_code}","message": f"{response.text}"}

            return {"code":"200","message": "Menú creado correctamente"}

        except Exception as e:
            raise Exception(str(e))

    raise Exception("Método no permitido")

def get_notas_alumno(request):
    token = obtener_token_acceso()
    uid = request.GET.get("uid")
    urlAlumno = f"{os.getenv('URL_ALUMNOS')}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

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
                            "referenceValue": urlAlumno
                        }
                    }
                }
            }
        }


            urlIndice = os.getenv('URL_INDICE')
            response = requests.post(urlIndice, headers=headers, json=query)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            notas_raw = response.json()
            notas = [
                    parse_notas_document(result["document"])
                    for result in notas_raw if "document" in result
                ]

            return {"code":"200", "message": notas}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["descripcion", "titulo", "tipoUser", "fecha", "alumno", "tipoNota"]
            campos_opcionales = ["fechaRecordatorio", "gravedad"]
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            faltantes = [campo for campo in campos_obligatorios if campo not in data]
            campos_invalidos = [campo for campo in data if campo not in campos_permitidos]


            if faltantes:
                return {
                    "code": "400",
                    "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"
                }
            
            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }

            if data.get("tipoUser") not in ["maestro", "usuario"]:
                return {"code": "400", "error": "tipoUser debe ser 'maestro' o 'usuario'"}

            if data.get("tipoNota") not in ["informacion", "recordatorio", "incidencia"]:
                return {"code": "400", "error": "tipoNota debe ser 'informacion', 'recordatorio' o 'incidencia'"}
            elif data.get("tipoNota") == "incidencia" and "gravedad" not in data:
                return {"code": "400", "error": "El campo 'gravedad' es obligatorio cuando tipoNota es 'incidencia'"}
            
            firestore_payload = transformar_a_firestore_fields(data)
            url_notas = os.getenv('URL_NOTAS')
            response = requests.post(url_notas, headers=headers, json=firestore_payload)
            if response.status_code not in [200, 201]:
                print("❌ ERROR al guardar nota en Firestore")
                print("🔢 Status:", response.status_code)
                print("📩 Payload enviado:", json.dumps(firestore_payload, indent=2))
                print("🧾 Respuesta de Firestore:", response.text)

                return {
                    "code": str(response.status_code),
                    "error": f"Firestore error: {response.text}"
                }


            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Nota añadida correctamente", "id": document_id}

        except Exception as e:
            traceback.print_exc()
            return {"code": "500", "error": str(e)}





def get_alumnos(request):
    token = obtener_token_acceso()
    base_url = f"{os.getenv('URL_INICIO')}{os.getenv('URL_ALUMNOS')}"
    uid = request.GET.get("uid")
    nombre = request.GET.get("nombre")
    apellidos = request.GET.get("apellidos")
    cumpleanios = request.GET.get("cumpleanios")
    url_uid = f"{base_url}{uid}"

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

            campos_obligatorios = ["apellidos", "edad", "cumpleanios", "genero", "idioma", "nombre"]
            campos_opcionales = ["alergias", "ausencias", "conflictos", "enfermedades", "consumo", "medicamentos", "mochilas", "necesidades", "rutinaSuenio"]
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            faltantes = [campo for campo in campos_obligatorios if campo not in data]
            campos_invalidos = [campo for campo in data if campo not in campos_permitidos]


            if faltantes:
                return {
                    "code": "400",
                    "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"
                }
            
            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }

            if data.get("genero") not in ["Mujer", "Hombre"]:
                return {"code": "400", "error": "genero debe ser 'Mujer' o 'Hombre'"}
            
            firestore_payload = transformar_a_firestore_fields(data)

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

            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar al alumno"}

            data = json.loads(request.body)

            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.patch(url_uid, headers=headers, json=firestore_payload)

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

            campos_obligatorios = ["descripcion", "fecha", "titulo"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]
            campos_invalidos = [campo for campo in data if campo not in campos_obligatorios]


            if faltantes:
                return {
                    "code": "400",
                    "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"
                }
            
            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }
            
            firestore_payload = transformar_a_firestore_fields(data)
            response = requests.post(base_url, headers=headers, json=firestore_payload)
            if response.status_code not in [200, 201]:
                return {
                    "code": str(response.status_code),
                    "error": f"Firestore error: {response.text}"
                }

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Noticia añadida correctamente", "id": document_id}

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
            firestore_payload = transformar_a_firestore_fields(data)

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


def get_medicamentos(request):
    token = obtener_token_acceso()
    base_url = os.getenv("URL_MEDICAMENTOS")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"

    if request.method == "GET":
        try:

            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
                if response.status_code != 200:
                    return {"code": "404", "error": f"No se encontró el medicamento con UID {uid}"}
                data = response.json()
                medicamento = parse_medicamento_document(data)
                return {"code": "200", "message": medicamento}
            else:
                response = requests.get(base_url, headers=headers)
                if response.status_code != 200:
                    return {"code": "500", "error": response.text}
                data = response.json()
                documentos = data.get("documents", [])
                medicamentos = [parse_medicamento_document(doc) for doc in documentos]
                return {"code": "200", "message": medicamentos}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            campos_obligatorios = ["nombre", "dosis", "horarioAdministracion", "frecuencia", "metodoAdministracion"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]
            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }

            try:
                data["horarioAdministracion"] = validar_horario_string(data["horarioAdministracion"])
            except ValueError as e:
                return {"code": "400", "error": str(e)}

            firestore_payload = transformar_a_firestore_fields(data)
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

    elif request.method == "PATCH":
        try:

            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar el medicamento"}

            data = json.loads(request.body)
            if "horarioAdministracion" in data:
                try:
                    data["horarioAdministracion"] = validar_horario_string(data["horarioAdministracion"])
                except ValueError as e:
                    return {"code": "400", "error": str(e)}

            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.patch(url_uid, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Medicamento '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar un medicamento"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Medicamento '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}

        
def get_alergias(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_ALERGIAS')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                alergia = parse_alergias_document(data)
                return {"code": "200", "message": alergia}
            else:
                documentos = data.get("documents", [])
                alergia = [parse_alergias_document(doc) for doc in documentos]
                return {"code": "200", "message": alergia}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["nombre", "tipo", "gravedad", "fechaDiagnostico", "reaccion", "tratamiento", "sintomas"]
            campos_opcionales = ["observaciones"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Alergia añadida correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar la alergia"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}


            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Alergia '{uid}' actualizada correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar una alergia"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Alergia '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


def get_enfermedades(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_ENFERMEDADES')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                enfermedad = parse_enfermedad_document(data)
                return {"code": "200", "message": enfermedad}
            else:
                documentos = data.get("documents", [])
                alergia = [parse_enfermedad_document(doc) for doc in documentos]
                return {"code": "200", "message": alergia}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["nombre", "contagiosa", "tratamiento", "gravedad", "descripcion"]
            campos_opcionales = ["observaciones"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Enfermedad añadida correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar la enfermedad"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Enfermedad '{uid}' actualizada correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar una enfermedad"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Enfermedad '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}



def get_necesidades(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_NECESIDADES')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                necesidad = parse_necesidad_document(data)
                return {"code": "200", "message": necesidad}
            else:
                documentos = data.get("documents", [])
                necesidad = [parse_necesidad_document(doc) for doc in documentos]
                return {"code": "200", "message": necesidad}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["tipo", "fecha", "ayuda"]
            campos_opcionales = ["comentarios"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Necesidad añadida correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar la necesidad"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Necesidad '{uid}' actualizada correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar una necesidad"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Necesidad '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


def get_conflictos(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_CONFLICTOS')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                conflicto = parse_conflicto_document(data)
                return {"code": "200", "message": conflicto}
            else:
                documentos = data.get("documents", [])
                conflicto = [parse_conflicto_document(doc) for doc in documentos]
                return {"code": "200", "message": conflicto}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["accion", "descripcion", "informado", "observaciones", "fecha", "resolucion", "motivo", "gravedad"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]


            return {"code": "201", "message": "Conflicto añadido correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar el conflicto"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Conflicto '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar un conflicto"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Conflicto '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}

def get_rutina(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_RUTINA')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                rutina = parse_suenio_document(data)
                return {"code": "200", "message": rutina}
            else:
                documentos = data.get("documents", [])
                rutina = [parse_suenio_document(doc) for doc in documentos]
                return {"code": "200", "message": rutina}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["comentarios", "fecha", "duracion"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]


            return {"code": "201", "message": "Rutina añadida correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar la rutina"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Rutina '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar una rutina"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Rutina '{uid}' eliminada correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}

import sys
import traceback

def get_mochilas(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_MOCHILAS')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(f"{base_url}{uid}", headers=headers)
                if response.status_code != 200:
                    return {"code": "500", "error": response.text}
                data = response.json()
                return {"code": "200", "data": parse_mochila_document(data)}
            else:
                response = requests.get(base_url, headers=headers)
                if response.status_code != 200:
                    return {"code": "500", "error": response.text}
                data = response.json()
                documentos = data.get("documents", [])
                mochilas = [parse_mochila_document(doc) for doc in documentos]
                return {"code": "200", "data": mochilas}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["fecha", "objetos"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]
            
            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}

            firestore_payload = transformar_a_firestore_fields(data)
            response = requests.post(base_url, headers=headers, json=firestore_payload)
            
            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}
            
            firestore_response = response.json() 
            document_path = firestore_response.get("name", "")
            document_id = document_path.split("/")[-1]

            return {"code": "201", "message": "Mochila añadida correctamente", "id": document_id}

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {
                "code": "500",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "file": exc_traceback.tb_frame.f_code.co_filename,
                "line": exc_traceback.tb_lineno,
                "function": exc_traceback.tb_frame.f_code.co_name
            }

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar la mochila"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Mochila '{uid}' actualizado correctamente"}

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {
                "code": "500",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "file": exc_traceback.tb_frame.f_code.co_filename,
                "line": exc_traceback.tb_lineno,
                "function": exc_traceback.tb_frame.f_code.co_name
            }
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar una rutina"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Mochila '{uid}' eliminada correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


def get_consumo(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_CONSUMO')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(url_uid, headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                consumo = parse_consumo_document(data)
                return {"code": "200", "message": consumo}
            else:
                documentos = data.get("documents", [])
                consumo = [parse_consumo_document(doc) for doc in documentos]
                return {"code": "200", "message": consumo}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["idPlato", "cantidad", "fecha", "comentarios"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]


            return {"code": "201", "message": "Consumo añadido correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar el consumo"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Consumo '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar un consumo"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Consumo '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}


def get_ausencias(request):
    token = obtener_token_acceso()
    base_url = os.getenv('URL_AUSENCIAS')
    uid = request.GET.get("uid")
    url_uid = f"{base_url}{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if request.method == "GET":
        try:
            if uid:
                response = requests.get(url_uid, headers=headers)
            else:
                response = requests.get(base_url, headers=headers)

            if response.status_code != 200:
                return {"code": "500", "error": response.text}

            data = response.json()

            if uid:
                ausencia = parse_ausencia_document(data)
                return {"code": "200", "message": ausencia}
            else:
                documentos = data.get("documents", [])
                ausencia = [parse_ausencia_document(doc) for doc in documentos]
                return {"code": "200", "message": ausencia}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            campos_obligatorios = ["notificado", "estado", "fechaNotificacion", "fecha", "comentarios", "motivo", "justificado"]
            campos_opcionales=["motivoJustificacion"]
            faltantes = [campo for campo in campos_obligatorios if campo not in data]

            if faltantes:
                return {"code": "400", "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
            
            campos_recibidos = set(data.keys())
            campos_permitidos = set(campos_obligatorios + campos_opcionales)
            campos_invalidos = campos_recibidos - campos_permitidos

            if campos_invalidos:
                return {
                    "code": "400",
                    "error": f"Campos no permitidos: {', '.join(campos_invalidos)}"
                }


            firestore_payload = transformar_a_firestore_fields(data)

            response = requests.post(base_url, headers=headers, json=firestore_payload)

            if response.status_code not in [200, 201]:
                return {"code": str(response.status_code), "error": response.text}

            doc = response.json()
            document_path = doc.get("name", "")
            document_id = document_path.split("/")[-1]


            return {"code": "201", "message": "Consumo añadido correctamente", "id": document_id}

        except Exception as e:
            return {"code": "500", "error": str(e)}

    elif request.method == "PATCH":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para actualizar el consumo"}

            data = json.loads(request.body)
            campos_actualizados = {}

            campos_actualizados = transformar_a_firestore_fields(data)

            if not campos_actualizados:
                return {"code": "400", "error": "No se proporcionaron campos para actualizar"}

            response = requests.patch(url_uid, headers=headers, json={"fields": campos_actualizados})

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}

            return {"code": "200", "message": f"Consumo '{uid}' actualizado correctamente"}

        except Exception as e:
            return {"code": "500", "error": str(e)}
    elif request.method == "DELETE":
        try:
            if not uid:
                return {"code": "400", "error": "Se requiere 'uid' para eliminar un consumo"}

            response = requests.delete(url_uid, headers=headers)

            if response.status_code not in [200, 204]:
                return {"code": str(response.status_code), "error": response.text}
            return {"code": "200", "message": f"Consumo '{uid}' eliminado correctamente"}
        except Exception as e:
            return {"code": "500", "error": str(e)}

    return {"code": "405", "error": "Método no permitido"}

