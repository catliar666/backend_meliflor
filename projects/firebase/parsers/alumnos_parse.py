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
    
    def resolve_alergias(refs):
        alergias = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))
                alergias.append(parse_alergias_document(raw_doc))
            except Exception as e:
                print(f"Error cargando alergia {ref}: {e}")
        return alergias

    alergia_refs = extract_refs(fields.get("alergias", {}))

    def resolve_medicamentos(refs):
        medicamentos = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))
                medicamentos.append(parse_medicamento_document(raw_doc))
            except Exception as e:
                print(f"Error cargando medicamentos {ref}: {e}")
        return medicamentos

    medicamentos_refs = extract_refs(fields.get("medicamentos", {}))

    def resolve_necesidades(refs):
        necesidades = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                necesidades.append(parse_necesidad_document(raw_doc))
            except Exception as e:
                print(f"Error cargando necesidades {ref}: {e}")
        return necesidades

    necesidades_refs = extract_refs(fields.get("necesidades", {}))

    def resolve_enfermedades(refs):
        enfermedades = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                enfermedades.append(parse_enfermedad_document(raw_doc))
            except Exception as e:
                print(f"Error cargando enfermedades {ref}: {e}")
        return enfermedades

    enfermedades_refs = extract_refs(fields.get("enfermedades", {}))

    def resolve_conflictos(refs):
        conflictos = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                conflictos.append(parse_conflicto_document(raw_doc))
            except Exception as e:
                print(f"Error cargando conflictos {ref}: {e}")
        return conflictos

    conflictos_refs = extract_refs(fields.get("conflictos", {}))

    def resolve_suenio(refs):
        suenio = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                suenio.append(parse_suenio_document(raw_doc))
            except Exception as e:
                print(f"Error cargando suenio {ref}: {e}")
        return suenio

    suenio_refs = extract_refs(fields.get("rutinaSuenio", {}))

    def resolve_ausencias(refs):
        ausencias = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                ausencias.append(parse_ausencia_document(raw_doc))
            except Exception as e:
                print(f"Error cargando ausencias {ref}: {e}")
        return ausencias

    ausencias_refs = extract_refs(fields.get("ausencias", {}))

    
    def resolve_mochilas(refs):
        mochilas = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                mochilas.append(parse_mochila_document(raw_doc))
            except Exception as e:
                print(f"Error cargando mochilas {ref}: {e}")
        return mochilas

    mochilas_refs = extract_refs(fields.get("mochilas", {}))

    def resolve_consumo(refs):
        consumo = []
        for ref in refs:
            try:
                raw_doc = fetch_document_by_reference(ref.lstrip("/"))  # quitar "/" inicial
                consumo.append(parse_consumo_document(raw_doc))
            except Exception as e:
                print(f"Error cargando consumo {ref}: {e}")
        return consumo

    consumo_refs = extract_refs(fields.get("consumo", {}))

    return {
        "nombre": fields.get("nombre", {}).get("stringValue", ""),
        "apellidos": fields.get("apellidos", {}).get("stringValue", ""),
        "genero": fields.get("genero", {}).get("stringValue", ""),
        "edad": fields.get("edad", {}).get("integerValue", ""),
        "idioma": fields.get("idioma", {}).get("stringValue", ""),
        "cumpleanios": fields.get("cumpleanios", {}).get("timestampValue", ""),
        "alergias": resolve_alergias(alergia_refs),
        "medicamentos": resolve_medicamentos(medicamentos_refs),
        "enfermedades": resolve_enfermedades(enfermedades_refs),
        "necesidades": resolve_necesidades(necesidades_refs),
        "conflictos": resolve_conflictos(conflictos_refs),
        "rutinaSuenio": resolve_suenio(suenio_refs),
        "ausencias": resolve_ausencias(ausencias_refs),
        "mochilas": resolve_mochilas(mochilas_refs),
        "consumo": resolve_consumo(consumo_refs),
    }
