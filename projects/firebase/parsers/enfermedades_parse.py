def parse_enfermedad_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "contagiosa": fields.get("contagiosa", {}).get("booleanValue", False),
        "tratamiento": fields.get("tratamiento", {}).get("stringValue", ""),
        "gravedad": fields.get("gravedad", {}).get("stringValue", ""),
        "observaciones": fields.get("observaciones", {}).get("stringValue", ""),
    }
