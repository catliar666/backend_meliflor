from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_conflicto_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "motivo": fields.get("motivo", {}).get("stringValue", ""),
        "gravedad": fields.get("gravedad", {}).get("stringValue", ""),
        "observaciones": fields.get("observaciones", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw),
        "informado": fields.get("informado", {}).get("booleanValue", False),
        "accion": fields.get("accion", {}).get("stringValue", ""),
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "resolucion": fields.get("resolucion", {}).get("stringValue", ""),
    }
