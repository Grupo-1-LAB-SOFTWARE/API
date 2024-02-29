from django.urls import path

from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    InstitutoView, CampusView, CursoView, AtividadeLetivaView, 
                    AtividadePedagogicaComplementarView, AtividadeOrientaçaoView, 
                    BancaExaminacaoView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('instituto/', InstitutoView.as_view(), name='instituto'),
    path('instituto/<int:instituto_id>', InstitutoView.as_view(), name='instituto_get_by_id'),
    path('campus/', CampusView.as_view(), name='campus'),
    path('campus/<int:campus_id>/', CampusView.as_view(), name='campus_get_by_id'),
    path('curso/', CursoView.as_view(), name='curso'),
    path('curso/<int:curso_id>', CursoView.as_view(), name='curso_get_by_id'),
    path('atividadeletiva/', AtividadeLetivaView.as_view(), name='atividadeletiva'),
    path('atividadepedagogicacomplementar/', AtividadePedagogicaComplementarView.as_view(), name='atividadepedagogicacomplementar'),
    path('atividadeorientacao/', AtividadeOrientaçaoView.as_view(), name='atividadeorientacao'),
    path('bancaexaminacao/', BancaExaminacaoView.as_view(), name='bancaexaminacao')
]