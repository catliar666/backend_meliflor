def parse_suenio_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "duracion": fields.get("duracion", {}).get("stringValue", ""),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", "")
    }
