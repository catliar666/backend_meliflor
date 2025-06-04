def parse_medicamento_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "dosis": fields.get("dosis", {}).get("stringValue", ""),
        "frecuencia": fields.get("frecuencia", {}).get("stringValue", ""),
        "metodoAdministracion": fields.get("metodoAdministracion", {}).get("stringValue", ""),
        "horarioAdministracion": fields.get("horarioAdministracion", {}).get("stringValue", ""),
    }
