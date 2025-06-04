def parse_notas_document(doc):
    fields = doc.get("fields", {})
    
    return {
        "id": doc["name"].split("/")[-1],
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
    }