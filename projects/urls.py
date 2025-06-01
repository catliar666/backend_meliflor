from django.urls import path
from .views import perfil_usuario, token, obtener_menu_semanal


urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', token, name="firestore_token"),
    path('usuarios/<str:uid>/', perfil_usuario, name='perfil_usuario'),
    path('menu/', obtener_menu_semanal, name='menus')
]

# urlpatterns += router.urls

