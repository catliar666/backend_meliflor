def parse_notas_document(doc):
    fields = doc.get("fields", {})
    
    return {
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
    }