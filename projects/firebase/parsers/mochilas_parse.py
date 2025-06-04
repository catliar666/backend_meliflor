from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_mochila_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "fecha": convertir_fecha_utc_a_local(fecha_raw),
        "objetos": [
            obj.get("stringValue", "")
            for obj in fields.get("objetos", {}).get("arrayValue", {}).get("values", [])
        ]
    }
