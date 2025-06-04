def parse_mochila_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
        "objetos": [
            obj.get("stringValue", "")
            for obj in fields.get("objetos", {}).get("arrayValue", {}).get("values", [])
        ]
    }
