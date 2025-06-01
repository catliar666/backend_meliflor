

from django.http import JsonResponse
from projects.firebase.auth import obtener_token_acceso
from .firebase.firebase_services import get_usuario_completo, get_administradores_completo, obtener_menu_de_la_semana, get_notas_alumno, get_alumnos, get_noticias
from .firebase.parsers.usuarios_parse import parse_usuario_document
from .firebase.parsers.alumnos_parse import parse_alumno_document
from django.views.decorators.csrf import csrf_exempt
# from .firebase_service import fetch_document_by_reference
import requests


def token(request):
    token = obtener_token_acceso()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return JsonResponse({"token": token})

@csrf_exempt
def perfil_usuario(request, uid):
    try:
        usuario = get_usuario_completo(request, uid)
        administrador = get_administradores_completo(uid)
        if usuario is None and administrador is None:
            return JsonResponse({'code': str('404'), 'error': str('Usuario no encontrado')}, status=404)
        elif usuario is not None: return JsonResponse(usuario, status=200)
        else: return JsonResponse(administrador, status=200)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)

@csrf_exempt   
def obtener_menu_semanal(request):
    try:
        menu = obtener_menu_de_la_semana(request)
        if menu is not None: return JsonResponse(menu, status=200, safe=False)
        else: return JsonResponse({'code': str('400'), 'error': str('No hay ningun menú para esta semana')}, status=404)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def obtener_notas_por_alumno(request, uid):
    try:
        notas = get_notas_alumno(request, uid)
        return JsonResponse(notas, status=200, safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def obtener_alumnos(request):
    try:
        alumnos = get_alumnos(request)
        return JsonResponse(alumnos, status=200, safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def obtener_noticias(request):
    try:
        noticias = get_noticias(request)
        return JsonResponse(noticias, status=200, safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)





