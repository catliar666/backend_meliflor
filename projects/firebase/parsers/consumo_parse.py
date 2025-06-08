from ..helpers import convertir_fecha_utc_a_local, fetch_document_by_reference

def parse_consumo_document(doc):
    fields = doc.get("fields", {})

    plato_ref = fields.get("idPlato", {}).get("referenceValue", "")
    plato_data = {}
    if plato_ref:
        try:
            plato_doc = fetch_document_by_reference(plato_ref)
            plato_fields = plato_doc.get("fields", {})
            plato_id = plato_doc.get("name", "").split("/")[-1]
            plato_nombre = plato_fields.get("nombre", {}).get("stringValue", "")
            plato_categoria = plato_fields.get("categoria", {}).get("stringValue", "")
            plato_data = {
                "id": plato_id,
                "nombre": plato_nombre,
                "categoria": plato_categoria
            }
        except Exception as e:
            print(f"Error al obtener el plato: {e}")
            plato_data = {}
    fecha_raw = fields.get("fecha", {}).get("timestampValue", "")
    return {
        "id": doc["name"].split("/")[-1],
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "cantidad": fields.get("cantidad", {}).get("stringValue", ""),
        "fecha": convertir_fecha_utc_a_local(fecha_raw),
        "plato": plato_data
    }
