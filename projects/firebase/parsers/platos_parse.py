def parse_plato_document(doc):
    fields = doc.get("fields", {})

    return {
        "id": doc.get("name", "").split("/")[-1],
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "descripcion": fields.get("descripcion", {}).get("stringValue", ""),
        "comentarios": fields.get("comentarios", {}).get("stringValue", ""),
        "categoria": fields.get("categoria", {}).get("stringValue", ""),
        "porciones": fields.get("porciones", {}).get("stringValue", ""),
        "calorias": fields.get("calorias", {}).get("stringValue", ""),
        "ingredientes": [
            item.get("stringValue", "") for item in fields.get("ingredientes", {}).get("arrayValue", {}).get("values", [])
        ],
        "alergenos": [
            item.get("stringValue", "") for item in fields.get("alergenos", {}).get("arrayValue", {}).get("values", [])
        ],
    }

