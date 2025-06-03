from ..helpers import fetch_document_by_reference

def parse_notificacion_document(doc):
    fields = doc.get("fields", {})

    def extract_ref(field):
        return field.get("referenceValue", "")

    def extract_id_from_ref(ref):
        return ref.rstrip("/").split("/")[-1]

    user_ref = extract_ref(fields.get("idUser", {}))
    user_id = extract_id_from_ref(user_ref) if user_ref else None

    return {
        "cuerpo": fields.get("cuerpo", {}).get("stringValue", ""),
        "idUser": user_id,
        "titulo": fields.get("titulo", {}).get("stringValue", ""),
        "leido": fields.get("leido", {}).get("booleanValue", ""),
        "ruta": fields.get("ruta", {}).get("stringValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", "")
    }
