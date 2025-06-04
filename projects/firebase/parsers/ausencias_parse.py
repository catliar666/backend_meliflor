from projects.firebase.helpers import convertir_fecha_utc_a_local


def parse_ausencia_document(doc):
    fields = doc.get("fields", {})
    fecha_raw = fields.get("fechaNotificacion", {}).get("timestampValue", "")
    fecha2_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "estado": fields.get("estado", {}).get("stringValue", ""),
        "fechaNotificacion": convertir_fecha_utc_a_local(fecha_raw),
        "fecha": convertir_fecha_utc_a_local(fecha2_raw),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "notificado": fields.get("notificado", {}).get("booleanValue", False),
        "motivoJustificacion": fields.get("motivoJustificacion", {}).get("stringValue", ""),
        "motivo": fields.get("motivo", {}).get("stringValue", ""),
        "justificado": fields.get("justificado", {}).get("booleanValue", False),
    }
