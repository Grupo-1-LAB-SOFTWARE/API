from django.urls import path
from .views import UsuarioView, AtivarContaView

urlpatterns = [
    path('registrar/', UsuarioView.as_view(), name='registrar'),
    path('ativar/<uidb64>/<token>/', AtivarContaView.as_view(), name='ativar_conta'),
]