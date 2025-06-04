from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_necesidad_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", ""),
    return {
        "id": doc["name"].split("/")[-1],
        "fecha": convertir_fecha_utc_a_local(fecha_raw),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "tipo": [
            t.get("stringValue", "")
            for t in fields.get("tipo", {}).get("arrayValue", {}).get("values", [])
        ],
        "ayuda": fields.get("ayuda", {}).get("booleanValue", False),
    }
