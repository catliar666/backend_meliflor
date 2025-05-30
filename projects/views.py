

from django.http import JsonResponse
from projects.firebase.auth import obtener_token_acceso
from .firebase.firebase_services import get_usuario_completo, get_administradores_completo, obtener_menu_de_la_semana
from .firebase.parsers.usuarios_parse import parse_usuario_document
from .firebase.parsers.alumnos_parse import parse_alumno_document
# from .firebase_service import fetch_document_by_reference
import requests


def token(request):
    token = obtener_token_acceso()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    # Tu lógica con Firestore
    return JsonResponse({"token": token})


def perfil_usuario(request, uid):
    try:
        usuario = get_usuario_completo(uid)
        administrador = get_administradores_completo(uid)
        if usuario is None and administrador is None:
            return JsonResponse({'code': str('404'), 'error': str('Usuario no encontrado')}, status=404)
        elif usuario is not None: return JsonResponse(usuario, status=200)
        else: return JsonResponse(administrador, status=200)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
def obtener_menu_semanal(request):
    try:
        menu = obtener_menu_de_la_semana()
        if menu is not None: return JsonResponse(menu, status=200, safe=False)
        else: return JsonResponse({'code': str('400'), 'error': str('No hay ningun menú para esta semana')}, status=404)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    




