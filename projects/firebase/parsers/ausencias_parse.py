def parse_ausencia_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc["name"].split("/")[-1],
        "estado": fields.get("estado", {}).get("stringValue", ""),
        "fechaNotificacion": fields.get("fechaNotificacion", {}).get("timestampValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "notificado": fields.get("notificado", {}).get("booleanValue", False),
        "motivoJustificacion": fields.get("motivoJustificacion", {}).get("stringValue", ""),
        "motivo": fields.get("motivo", {}).get("stringValue", ""),
        "justificado": fields.get("justificado", {}).get("booleanValue", False),
    }
