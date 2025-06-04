from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_noticia_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc.get("name", "").split("/")[-1],
        "titulo": fields.get("titulo", {}).get("stringValue", ""),
        "foto": fields.get("foto", {}).get("stringValue", ""),
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw)
    }
