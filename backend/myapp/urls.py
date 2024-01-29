from django.urls import path
from .views import UsuarioView, ActivateEmail

urlpatterns = [
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('registrar/', UsuarioView.as_view(), name='registrar'),
    path('activate/<str:login>/', ActivateEmail.as_view(), name='activate'),
]