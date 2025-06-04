from ..helpers import fetch_document_by_reference
from .alergias_parse import parse_alergias_document
from .medicamentos_parse import parse_medicamento_document
from .enfermedades_parse import parse_enfermedad_document
from .necesidades_parse import parse_necesidad_document
from .conflictos_parse import parse_conflicto_document
from .suenio_parse import parse_suenio_document
from .ausencias_parse import parse_ausencia_document
from .mochilas_parse import parse_mochila_document
from .consumo_parse import parse_consumo_document

def parse_alumno_document(doc):
    fields = doc.get("fields", {})

    def extract_refs(field):
        return [item.get("referenceValue", "") for item in field.get("arrayValue", {}).get("values", [])]
    
    def extract_id_from_ref(refs):
        return [ref.rstrip("/").split("/")[-1] for ref in refs]

    
    alergias_ref = extract_refs(fields.get("alergias", {}))
    alergias_id = extract_id_from_ref(alergias_ref) if alergias_ref else None

    medicamentos_ref = extract_refs(fields.get("medicamentos", {}))
    medicamentos_id = extract_id_from_ref(medicamentos_ref) if medicamentos_ref else None

    enfermedades_ref = extract_refs(fields.get("enfermedades", {}))
    enfermedades_id = extract_id_from_ref(enfermedades_ref) if enfermedades_ref else None

    medicamentos_ref = extract_refs(fields.get("alergias", {}))
    medicamentos_id = extract_id_from_ref(alergias_ref) if alergias_ref else None

    necesidades_ref = extract_refs(fields.get("necesidades", {}))
    necesidades_id = extract_id_from_ref(necesidades_ref) if necesidades_ref else None

    conflictos_ref = extract_refs(fields.get("conflictos", {}))
    conflictos_id = extract_id_from_ref(conflictos_ref) if conflictos_ref else None

    rutinaSuenio_ref = extract_refs(fields.get("rutinaSuenio", {}))
    rutinaSuenio_id = extract_id_from_ref(rutinaSuenio_ref) if rutinaSuenio_ref else None

    ausencias_ref = extract_refs(fields.get("ausencias", {}))
    ausencias_id = extract_id_from_ref(ausencias_ref) if ausencias_ref else None

    mochilas_ref = extract_refs(fields.get("mochilas", {}))
    mochilas_id = extract_id_from_ref(mochilas_ref) if mochilas_ref else None

    consumo_ref = extract_refs(fields.get("consumo", {}))
    consumo_id = extract_id_from_ref(consumo_ref) if consumo_ref else None

    return {
        "id": doc["name"].split("/")[-1],
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "apellidos": fields.get("apellidos", {}).get("stringValue", ""),
        "genero": fields.get("genero", {}).get("stringValue", ""),
        "edad": fields.get("edad", {}).get("integerValue", ""),
        "idioma": fields.get("idioma", {}).get("stringValue", ""),
        "cumpleanios": fields.get("cumpleanios", {}).get("timestampValue", ""),
        "alergias": alergias_id,
        "medicamentos": medicamentos_id,
        "enfermedades": enfermedades_id,
        "necesidades": necesidades_id,
        "conflictos": conflictos_id,
        "rutinaSuenio": rutinaSuenio_id,
        "ausencias": ausencias_id,
        "mochilas": mochilas_id,
        "consumo": consumo_id,
    }
