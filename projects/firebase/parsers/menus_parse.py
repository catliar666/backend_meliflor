from ..helpers import fetch_document_by_reference
from .platos_parse import parse_plato_document

def parse_menu_document(doc):
    fields = doc.get("fields", {})

    def extract_refs(field):
        return [item.get("referenceValue", "") for item in field.get("arrayValue", {}).get("values", [])]

    def resolve_platos(refs):
        platos = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))
                platos.append(parse_plato_document(raw_doc))
            except Exception as e:
                print(f"Error cargando platos {ref}: {e}")
        return platos
    
    platos_refs = extract_refs(fields.get("platos", {}))

    return {
        "id": doc.get("name", "").split("/")[-1],
        "fechaComienzo": fields.get("fechaComienzo", {}).get("timestampValue", ""),
        "fechaFin": fields.get("fechaFin", {}).get("timestampValue", ""),
        "platos":  resolve_platos(platos_refs),
    }

