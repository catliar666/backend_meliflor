from ..helpers import convertir_fecha_utc_a_local, fetch_document_by_reference
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
    fecha_comienzo_raw = fields.get("fechaComienzo", {}).get("timestampValue", "")
    fecha_fin_raw = fields.get("fechaFin", {}).get("timestampValue", "")

    return {
        "id": doc.get("name", "").split("/")[-1],
        "fechaComienzo": convertir_fecha_utc_a_local(fecha_comienzo_raw),  # Ajustada
        "fechaFin": convertir_fecha_utc_a_local(fecha_fin_raw),            # Ajustada
        "platos": resolve_platos(platos_refs),
    }


