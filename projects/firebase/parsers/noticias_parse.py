def parse_noticia_document(doc):
    fields = doc.get("fields", {})
    
    return {
        "id": doc.get("name", "").split("/")[-1],
        "titulo": fields.get("titulo", {}).get("stringValue", ""),
        "foto": fields.get("foto", {}).get("stringValue", ""),
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
    }
