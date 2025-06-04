from django.urls import path
from .views import usuario, token, menu_semanal, notas_por_alumno, alumnos, noticias, notifications, medicamentos, alergias, enfermedades, necesidades, conflictos, rutinaSuenio, ausencias, mochilas, consumo


urlpatterns = [
    path('token/', token, name="firestore_token"),
    path('usuarios/<str:uid>/', usuario, name='perfil_usuario'),
    path('menu/', menu_semanal, name='menus'),
    path('notas/<str:uid>/', notas_por_alumno, name='notas_por_alumno'),
    path('alumnos/', alumnos, name='alumnos'),
    path('noticias/', noticias, name='noticias'),
    path('notification/', notifications, name='enviar_notificacion'),
    path('medicamentos/', medicamentos, name='medicamentos'),
    path('alergias/', alergias, name='alergias'),
    path('enfermedades/', enfermedades, name='enfermedades'),
    path('necesidades/', necesidades, name='necesidades'),
    path('conflictos/', conflictos, name='conflictos'),
    path('ausencias/', ausencias, name='ausencias'),
    path('mochilas/', mochilas, name='mochilas'),
    path('consumo/', consumo, name='consumo')
]

# urlpatterns += router.urls

