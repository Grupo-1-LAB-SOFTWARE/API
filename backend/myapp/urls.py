from django.urls import path
from .views import UsuarioView, ActivateEmail, LoginView, AtividadeLetivaView

urlpatterns = [
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('activate/<str:login>/', ActivateEmail.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('atividadeletiva/', AtividadeLetivaView.as_view(), name='atividadeletiva')
]