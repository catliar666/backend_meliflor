from ..helpers import fetch_document_by_reference

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
            plato_data = {
                "id": plato_id,
                "nombre": plato_nombre
            }
        except Exception as e:
            print(f"Error al obtener el plato: {e}")
            plato_data = {}

    return {
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "cantidad": fields.get("cantidad", {}).get("stringValue", ""),
        "fecha": fields.get("fecha", {}).get("timestampValue", ""),
        "plato": plato_data
    }
