from django.urls import path
from .views import perfil_usuario, token, obtener_menu_semanal, obtener_notas_por_alumno


urlpatterns = [
    path('token/', token, name="firestore_token"),
    path('usuarios/<str:uid>/', perfil_usuario, name='perfil_usuario'),
    path('menu/', obtener_menu_semanal, name='menus'),
    path('notas/<str:uid>/', obtener_notas_por_alumno, name='notas_por_alumno'),

]

# urlpatterns += router.urls

