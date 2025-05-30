def parse_administrador_document(doc):
    fields = doc.get("fields", {})
    
    return {
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "apellidos": fields.get("apellidos", {}).get("stringValue", ""),
        "telefono": fields.get("telefono", {}).get("stringValue", ""),
        "estado": fields.get("estado", {}).get("stringValue", ""),
        "rol": fields.get("rol", {}).get("stringValue", ""),
        "direccion": fields.get("direccion", {}).get("stringValue", "")
    }
