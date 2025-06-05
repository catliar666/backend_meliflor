from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_notas_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    fecha2_raw = fields.get("fechaRecordatorio", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw),
        "fechaRecordatorio": convertir_fecha_utc_a_local(fecha2_raw),
        "titulo": fields.get("titulo", {}).get("stringValue", ""),
        "tipoNota": fields.get("tipoNota", {}).get("stringValue", ""),
        "tipoUser": fields.get("tipoUser", {}).get("stringValue", ""),
        "gravedad": fields.get("gravedad", {}).get("stringValue", "")
    }