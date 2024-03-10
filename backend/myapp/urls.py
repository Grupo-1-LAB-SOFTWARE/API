from django.urls import path

from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    RelatorioDocenteView, AtividadeLetivaView, CalculoCHSemanalAulasView, AtividadePedagogicaComplementarView, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    
    path('usuarios', UsuarioView.as_view(), name='usuarios'),

    path('usuarios/', UsuarioView.as_view(), name='usuarios/'),

    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),

    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),

    path('login', LoginView.as_view(), name='login'),

    path('login/', LoginView.as_view(), name='login/'),

    path('relatorio_docente', RelatorioDocenteView.as_view(), name='relatorio_docente'),

    path('relatorio_docente/', RelatorioDocenteView.as_view(), name='relatorio_docente/'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva/'),

    path('atividade_letiva/<int:id>/', AtividadeLetivaView.as_view(), name='atividade_letiva_get_by_id'),

    path('relatorio_docente/<int:id>/', RelatorioDocenteView.as_view(), name='relatorio_docente_get_by_id'),

    path('calculo_ch_semanal_aulas/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas/'),

    path('calculo_ch_semanal_aulas', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas'),

    path('calculo_ch_semanal_aulas/<int:id>/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas_get_by_id'),

    path('atividade_pedagogica_complementar', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar'),

    path('atividade_pedagogica_complementar/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/'),

    path('atividade_pedagogica_complementar/<int:id>/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar_get_by_id'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/<int:id>/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria_get_by_id'),
    
]