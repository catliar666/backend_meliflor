from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_notas_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw)
    }