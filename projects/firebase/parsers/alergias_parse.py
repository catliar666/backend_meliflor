def parse_alergias_document(doc):
    fields = doc.get("fields", {})
    return {
        "id": doc["name"].split("/")[-1],
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "tipo": fields.get("tipo", {}).get("stringValue", ""),
        "sintomas": [s.get("stringValue", "") for s in fields.get("sintomas", {}).get("arrayValue", {}).get("values", [])],
        "tratamiento": fields.get("tratamiento", {}).get("stringValue", ""),
        "gravedad": fields.get("gravedad", {}).get("stringValue", ""),
        "reaccion": fields.get("reaccion", {}).get("stringValue", ""),
        "fechaDiagnostico": fields.get("fechaDiagnostico", {}).get("timestampValue", ""),
        "observaciones": fields.get("observaciones", {}).get("stringValue", "")
    }
