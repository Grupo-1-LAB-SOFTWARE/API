from django.urls import path

#from backend.myapp.models import AtividadePedagogicaComplementar
from .views import UsuarioView, ActivateEmail, LoginView, AtividadeLetivaView, AtividadePedagogicaComplementarView, AtividadeOrientaçaoView, BancaExaminacaoView

urlpatterns = [
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('activate/<str:login>/', ActivateEmail.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('atividadeletiva/', AtividadeLetivaView.as_view(), name='atividadeletiva'),
    path('atividadepedagogicacomplementar/', AtividadePedagogicaComplementarView.as_view(), name='atividadepedagogicacomplementar'),
    path('atividadeorientacao/', AtividadeOrientaçaoView.as_view(), name='atividadeorientacao'),
    path('bancaexaminacao/', BancaExaminacaoView.as_view(), name='bancaexaminacao')
]