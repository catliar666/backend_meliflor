

from django.http import JsonResponse
from projects.firebase.auth import obtener_token_acceso
from .firebase.firebase_services import get_usuario_completo, get_administradores_completo, obtener_menu_de_la_semana, get_enfermedades, get_notas_alumno, get_alumnos, get_noticias, enviar_notificacion, get_medicamentos, get_alergias, get_necesidades, get_conflictos, get_rutina, get_mochilas, get_consumo, get_ausencias
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
def usuario(request):
    try:
        usuario = get_usuario_completo(request)
        administrador = get_administradores_completo(request)
        if usuario is None and administrador is None:
            return JsonResponse({'code': str('404'), 'error': str('Usuario no encontrado')}, status=404)
        elif usuario is not None: return JsonResponse(usuario, status=usuario['code'])
        else: return JsonResponse(administrador, status=usuario['code'])
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)

@csrf_exempt   
def menu_semanal(request):
    try:
        menu = obtener_menu_de_la_semana(request)
        if menu is not None: return JsonResponse(menu, status=menu['code'], safe=False)
        else: return JsonResponse({'code': str(menu['404']), 'error': str('No hay ningun menú para esta semana')}, status=menu['code'])
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def notas_por_alumno(request):
    try:
        notas = get_notas_alumno(request)
        return JsonResponse(notas, status=notas['code'], safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def alumnos(request):
    try:
        alumnos = get_alumnos(request)
        return JsonResponse(alumnos, status=alumnos['code'], safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def noticias(request):
    try:
        noticias = get_noticias(request)
        return JsonResponse(noticias, status=noticias['code'], safe=False)
    except Exception as e:
        return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)

@csrf_exempt
def notifications(request):
    try:
        notification = enviar_notificacion(request)
        return JsonResponse(notification, status=notification['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def medicamentos(request):
    try:
        medicamentos = get_medicamentos(request)
        return JsonResponse(medicamentos, status=medicamentos['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def alergias(request):
    try:
        alergias = get_alergias(request)
        return JsonResponse(alergias, status=alergias['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def enfermedades(request):
    try:
        enfermedades = get_enfermedades(request)
        return JsonResponse(enfermedades, status=enfermedades['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def necesidades(request):
    try:
        necesidades = get_necesidades(request)
        return JsonResponse(necesidades, status=necesidades['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def conflictos(request):
    try:
        conflictos =  get_conflictos(request)
        return JsonResponse(conflictos, status=conflictos['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def rutinaSuenio(request):
    try:
        rutinaSuenio =  get_rutina(request)
        return JsonResponse(rutinaSuenio, status=rutinaSuenio['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def ausencias(request):
    try:
        ausencias =  get_ausencias(request)
        return JsonResponse(ausencias, status=ausencias['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def mochilas(request):
    try:
        mochilas =  get_mochilas(request)
        return JsonResponse(mochilas, status=ausencias['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    
@csrf_exempt
def consumo(request):
    try:
        consumo =  get_consumo(request)
        return JsonResponse(consumo, status=consumo['code'], safe=False)
    except Exception as e:
         return JsonResponse({'code': str('500'), 'error': str(e)}, status=500)
    




