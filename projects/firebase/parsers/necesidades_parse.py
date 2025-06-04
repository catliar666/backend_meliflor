def parse_necesidad_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "tipo": [
            t.get("stringValue", "")
            for t in fields.get("tipo", {}).get("arrayValue", {}).get("values", [])
        ],
        "ayuda": fields.get("ayuda", {}).get("booleanValue", False),
    }
