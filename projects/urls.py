from django.urls import path
from .views import usuario, token, menu_semanal, notas_por_alumno, alumnos, noticias, notifications, medicamentos, alergias


urlpatterns = [
    path('token/', token, name="firestore_token"),
    path('usuarios/<str:uid>/', usuario, name='perfil_usuario'),
    path('menu/', menu_semanal, name='menus'),
    path('notas/<str:uid>/', notas_por_alumno, name='notas_por_alumno'),
    path('alumnos/', alumnos, name='alumnos'),
    path('noticias/', noticias, name='noticias'),
    path('notification/', notifications, name='enviar_notificacion'),
    path('medicamentos/', medicamentos, name='medicamentos'),
    path('alergias/', alergias, name='alergias')
]

# urlpatterns += router.urls

