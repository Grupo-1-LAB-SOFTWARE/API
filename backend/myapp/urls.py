from django.urls import path
from .views import UsuarioView, AtivarContaView, UsuariosTesteView

urlpatterns = [
    path('usuarios/', UsuariosTesteView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuariosTesteView.as_view(), name='usuarios_get_by_id'),
    path('registrar/', UsuarioView.as_view(), name='registrar'),
    path('ativar/<uidb64>/<token>/', AtivarContaView.as_view(), name='ativar_conta'),
]