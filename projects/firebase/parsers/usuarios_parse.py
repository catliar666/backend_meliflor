def parse_usuario_document(doc):
    fields = doc.get("fields", {})

    def extract_array(field, key="stringValue"):
        return [item.get(key, "") for item in field.get("arrayValue", {}).get("values", [])]

    def extract_timestamps(field):
        return [item.get("timestampValue", "") for item in field.get("arrayValue", {}).get("values", [])]

    def extract_ids_from_references(field):
        values = field.get("arrayValue", {}).get("values", [])
        ids = []
        for item in values:
            ref = item.get("referenceValue", "")
            if ref:
                ids.append(ref.rstrip("/").split("/")[-1])
        return ids

    return {
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "apellidos": fields.get("apellidos", {}).get("stringValue", ""),
        "dni": fields.get("dni", {}).get("stringValue", ""),
        "telefono": fields.get("telefono", {}).get("integerValue", ""),
        "telefonoEmergencia": fields.get("telefonoEmergencia", {}).get("integerValue", ""),
        "direccion": fields.get("direccion", {}).get("stringValue", ""),
        "genero": fields.get("genero", {}).get("stringValue", ""),
        "ocupacion": fields.get("ocupacion", {}).get("stringValue", ""),
        "nacionalidad": fields.get("nacionalidad", {}).get("stringValue", ""),
        "estadoCivil": fields.get("estadoCivil", {}).get("stringValue", ""),
        "fechaInscripcion": fields.get("fechaInscripcion", {}).get("timestampValue", ""),
        "role": fields.get("role", {}).get("stringValue", ""),
        "suscripcion": fields.get("suscripcion", {}).get("stringValue", ""),
        "autorizacionFotos": fields.get("autorizacionFotos", {}).get("booleanValue", False),
        "autorizacionExcursiones": fields.get("autorizacionExcursiones", {}).get("booleanValue", False),
        "custodia": fields.get("custodia", {}).get("booleanValue", False),
        "seguroMedico": fields.get("seguroMedico", {}).get("booleanValue", False),
        "cuotaPagada": extract_timestamps(fields.get("cuotaPagada", {})),
        "hijos": extract_ids_from_references(fields.get("hijos", {}))
    }

