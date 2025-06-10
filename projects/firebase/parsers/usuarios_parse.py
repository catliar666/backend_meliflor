from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_usuario_document(doc):
    fields = doc.get("fields", {})

    def get_value(field, key, default=""):
        return field.get(key, default)

    def extract_array(field, key="stringValue"):
        return [item.get(key, "") for item in field.get("arrayValue", {}).get("values", [])]

    def extract_timestamps(field):
        return [
            item.get("timestampValue", "")
            for item in field.get("arrayValue", {}).get("values", [])
            if item.get("timestampValue")
        ]

    def extract_ids_from_references(field):
        values = field.get("arrayValue", {}).get("values", [])
        ids = []
        for item in values:
            ref = item.get("referenceValue", "")
            if ref:
                ids.append(ref.rstrip("/").split("/")[-1])
        return ids

    fecha_raw = fields.get("fechaInscripcion", {}).get("timestampValue", "")

    tokens_fcm = extract_array(fields.get("tokenFCM", {})) if "tokenFCM" in fields else []
                                                    
    return {
        "id": doc["name"].split("/")[-1],
        "nombre": get_value(fields.get("nombre", {}), "stringValue"),
        "apellidos": get_value(fields.get("apellidos", {}), "stringValue"),
        "dni": get_value(fields.get("dni", {}), "stringValue"),
        "telefono": get_value(fields.get("telefono", {}), "integerValue"),
        "telefonoEmergencia": get_value(fields.get("telefonoEmergencia", {}), "integerValue"),
        "direccion": get_value(fields.get("direccion", {}), "stringValue"),
        "genero": get_value(fields.get("genero", {}), "stringValue"),
        "ocupacion": get_value(fields.get("ocupacion", {}), "stringValue"),
        "nacionalidad": get_value(fields.get("nacionalidad", {}), "stringValue"),
        "estadoCivil": get_value(fields.get("estadoCivil", {}), "stringValue"),
        "fechaInscripcion": convertir_fecha_utc_a_local(fecha_raw),
        "role": get_value(fields.get("role", {}), "stringValue"),
        "suscripcion": get_value(fields.get("suscripcion", {}), "stringValue"),
        "autorizacionFotos": fields.get("autorizacionFotos", {}).get("booleanValue", False),
        "autorizacionExcursiones": fields.get("autorizacionExcursiones", {}).get("booleanValue", False),
        "custodia": fields.get("custodia", {}).get("booleanValue", False),
        "seguroMedico": fields.get("seguroMedico", {}).get("booleanValue", False),
        "tokenFCM": tokens_fcm,
        "cuotaPagada": [
            convertir_fecha_utc_a_local(fecha)
            for fecha in extract_timestamps(fields.get("cuotaPagada", {}))
        ],
        "hijos": extract_ids_from_references(fields.get("hijos", {}))
    }


