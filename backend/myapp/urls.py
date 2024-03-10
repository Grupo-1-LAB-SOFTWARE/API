from django.urls import path

from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    RelatorioDocenteView, AtividadeLetivaView, CalculoCHSemanalAulasView, AtividadePedagogicaComplementarView, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView, DescricaoOrientacaoCoorientacaoAcademicaView, SupervisaoAcademicaView, PreceptoriaTutoriaResidenciaView, ExtrairDadosAtividadesLetivasPDFAPIView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    
    path('usuarios', UsuarioView.as_view(), name='usuarios'),

    path('usuarios/', UsuarioView.as_view(), name='usuarios/'),

    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios/id'),

    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),

    path('login', LoginView.as_view(), name='login'),

    path('login/', LoginView.as_view(), name='login/'),

    path('atividade_letiva', AtividadeLetivaView.as_view(), name='atividade_letiva'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva/'),

    path('atividade_letiva/<int:id>/', AtividadeLetivaView.as_view(), name='atividade_letiva/id'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva/'),

    path('atividade_letiva/<int:id>/', AtividadeLetivaView.as_view(), name='atividade_letiva/id'),

    path('relatorio_docente', RelatorioDocenteView.as_view(), name='relatorio_docente'),

    path('relatorio_docente/', RelatorioDocenteView.as_view(), name='relatorio_docente/'),

    path('relatorio_docente/<int:id>/', RelatorioDocenteView.as_view(), name='relatorio_docente/id'),

    path('calculo_ch_semanal_aulas/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas/'),

    path('calculo_ch_semanal_aulas', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas'),

    path('calculo_ch_semanal_aulas/<int:id>/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas/id'),

    path('atividade_pedagogica_complementar', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar'),

    path('atividade_pedagogica_complementar/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/'),

    path('atividade_pedagogica_complementar/<int:id>/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/id'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/<int:id>/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/id'),

    path('descricao_orientacao_coorientacao_academica', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica'),

    path('descricao_orientacao_coorientacao_academica/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/'),

    path('descricao_orientacao_coorientacao_academica/<int:id>/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/id'),

    path('supervisao_academica', SupervisaoAcademicaView.as_view(), name='supervisao_academica'),
    
    path('supervisao_academica/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/'),

    path('supervisao_academica/<int:id>/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/id'),

    path('preceptoria_tutoria_residencia', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia'),

    path('preceptoria_tutoria_residencia/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/'),

    path('preceptoria_tutoria_residencia/<int:id>/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/id'),
    path('extrair_dados_atividades_letivas', ExtrairDadosAtividadesLetivasPDFAPIView.as_view(), name='extrair_dados_atividades_letivas'),
]