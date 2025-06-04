from ..helpers import convertir_fecha_utc_a_local, fetch_document_by_reference

def parse_notificacion_document(doc):
    fields = doc.get("fields", {})

    def extract_ref(field):
        return field.get("referenceValue", "")

    def extract_id_from_ref(ref):
        return ref.rstrip("/").split("/")[-1]

    user_ref = extract_ref(fields.get("idUser", {}))
    user_id = extract_id_from_ref(user_ref) if user_ref else None

    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "cuerpo": fields.get("cuerpo", {}).get("stringValue", ""),
        "idUser": user_id,
        "titulo": fields.get("titulo", {}).get("stringValue", ""),
        "leido": fields.get("leido", {}).get("booleanValue", ""),
        "ruta": fields.get("ruta", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw)
    }
