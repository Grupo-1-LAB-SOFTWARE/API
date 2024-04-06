from django.urls import path

from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    RelatorioDocenteAdminView, RelatorioDocenteView, AtividadeLetivaView, AtividadePedagogicaComplementarView, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView, DescricaoOrientacaoCoorientacaoAcademicaView, SupervisaoAcademicaView, PreceptoriaTutoriaResidenciaView, BancaExaminadoraView, AvaliacaoDiscenteView, ProjetoPesquisaProducaoIntelectualView, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView, LivroCapituloVerbetePublicadoView, TrabalhoCompletoResumoPublicadoApresentadoCongressosView, OutraAtividadePesquisaProducaoIntelectualView, CHSemanalAtividadesPesquisaView, ProjetoExtensaoView, EstagioExtensaoView, AtividadeEnsinoNaoFormalView, OutraAtividadeExtensaoView, CHSemanalAtividadesExtensaoView, DistribuicaoCHSemanalView, AtividadeGestaoRepresentacaoView, QualificacaoDocenteAcademicaProfissionalView, OutraInformacaoView, AfastamentoView, DocumentoComprobatorioView, DownloadRelatorioDocenteView, CriarUsuarioView, UsuarioAdminView, ExtrairDadosAtividadesLetivasPDFAPIView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    
    path('usuarios', UsuarioView.as_view(), name='usuarios'),

    path('usuarios/', UsuarioView.as_view(), name='usuarios/'),

    path('usuarios/admin', UsuarioAdminView.as_view(), name='usuarios/admin'),

    path('usuarios/admin/', UsuarioAdminView.as_view(), name='usuarios/admin/'),

    path('usuarios/admin/<str:username>/', UsuarioAdminView.as_view(), name='usuarios/admin/id/'),

    path('usuarios/criar', CriarUsuarioView.as_view(), name='usuarios/criar'),
    
    path('usuarios/criar/', CriarUsuarioView.as_view(), name='usuarios/criar/'),

    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),

    path('login', LoginView.as_view(), name='login'),

    path('login/', LoginView.as_view(), name='login/'),

    path('atividade_letiva/<str:nome_relatorio>/', AtividadeLetivaView.as_view(), name='atividade_letiva/nome_relatorio/'),

    path('atividade_letiva/<str:nome_relatorio>/<int:id_atividade_letiva>/', AtividadeLetivaView.as_view(), name='atividade_letiva/nome_relatorio/id_atividade_letiva/'),

    path('relatorio_docente/admin', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin'),

    path('relatorio_docente/admin/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/'),

    path('relatorio_docente/admin/<int:id>/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/id/'),

    path('relatorio_docente/admin/usuario/<int:user_id>/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/usuario/id/'),

    path('relatorio_docente', RelatorioDocenteView.as_view(), name='relatorio_docente'),

    path('relatorio_docente/', RelatorioDocenteView.as_view(), name='relatorio_docente/'),

    path('relatorio_docente/<str:nome>/', RelatorioDocenteView.as_view(), name='relatorio_docente/nome/'),

    path('atividade_pedagogica_complementar/<str:nome_relatorio>/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/nome_relatorio/'),

    path('atividade_pedagogica_complementar/<str:nome_relatorio>/<int:id_atividade_pedagogica_complementar>/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/nome_relatorio/id_atividade_pedagogica_complementar/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/<str:nome_relatorio>/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/nome_relatorio/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/<str:nome_relatorio>/<int:id_atividade_orientacao_supervisao_preceptoria_tutoria>/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/nome_relatorio/id_atividade_orientacao_supervisao_preceptoria_tutoria/'),
    
    path('descricao_orientacao_coorientacao_academica/<str:nome_relatorio>/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/nome_relatorio/'),

    path('descricao_orientacao_coorientacao_academica/<str:nome_relatorio>/<int:id_descricao_orientacao_coorientacao_academica>/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/nome_relatorio/id_descricao_orientacao_coorientacao_academica/'),

    path('supervisao_academica/<str:nome_relatorio>/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/nome_relatorio/'),

    path('supervisao_academica/<str:nome_relatorio>/<int:id_supervisao_academica>/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/nome_relatorio/id_supervisao_academica/'),
    
    path('preceptoria_tutoria_residencia/<str:nome_relatorio>/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/nome_relatorio/'),

    path('preceptoria_tutoria_residencia/<str:nome_relatorio>/<int:id_preceptoria_tutoria_residencia>/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/nome_relatorio/id_preceptoria_tutoria_residencia/'),

    path('banca_examinadora/<str:nome_relatorio>/', BancaExaminadoraView.as_view(), name='banca_examinadora/nome_relatorio/'),

    path('banca_examinadora/<str:nome_relatorio>/<int:id_banca_examinadora>/', BancaExaminadoraView.as_view(), name='banca_examinadora/nome_relatorio/id_banca_examinadora/'),

    path('avaliacao_discente/<str:nome_relatorio>/', AvaliacaoDiscenteView.as_view(), name='avaliacao_discente/nome_relatorio/'),

    path('avaliacao_discente/<str:nome_relatorio>/<int:id_avaliacao_discente>/', AvaliacaoDiscenteView.as_view(), name='avaliacao_discente/nome_relatorio/id_avaliacao_discente/'),
   
    path('projeto_pesquisa_producao_intelectual/<str:nome_relatorio>/', ProjetoPesquisaProducaoIntelectualView.as_view(), name='projeto_pesquisa_producao_intelectual/nome_relatorio'),

    path('projeto_pesquisa_producao_intelectual/<str:nome_relatorio>/<int:id_projeto_pesquisa_producao_intelectual>/', ProjetoPesquisaProducaoIntelectualView.as_view(), name='projeto_pesquisa_producao_intelectual/nome_relatorio/id_projeto_pesquisa_producao_intelectual'),

    path('trabalho_completo_publicado_periodico_boletim_tecnico/<str:nome_relatorio>/', TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView.as_view(), name='trabalho_completo_publicado_periodico_boletim_tecnico/nome_relatorio'),

    path('trabalho_completo_publicado_periodico_boletim_tecnico/<str:nome_relatorio>/<int:id_trabalho_completo_publicado_periodico_boletim_tecnico>', TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView.as_view(), name='trabalho_completo_publicado_periodico_boletim_tecnico/nome_relatorio/id_trabalho_completo_publicado_periodico_boletim_tecnico/'),

    path('livro_capitulo_verbete_publicado/<str:nome_relatorio>/', LivroCapituloVerbetePublicadoView.as_view(), name='livro_capitulo_verbete_publicado/nome_relatorio'),

    path('livro_capitulo_verbete_publicado/<str:nome_relatorio>/<int:id_livro_capitulo_verbete_publicado>/', LivroCapituloVerbetePublicadoView.as_view(), name='livro_capitulo_verbete_publicado/nome_relatorio/id_livro_capitulo_verbete_publicado/'),

    path('trabalho_completo_resumo_publicado_apresentado_congressos/<str:nome_relatorio>/', TrabalhoCompletoResumoPublicadoApresentadoCongressosView.as_view(), name='trabalho_completo_resumo_publicado_apresentado_congressos/nome_relatorio'),

    path('trabalho_completo_resumo_publicado_apresentado_congressos/<str:nome_relatorio>/<int:id_trabalho_completo_resumo_publicado_apresentado_congressos>/', TrabalhoCompletoResumoPublicadoApresentadoCongressosView.as_view(), name='trabalho_completo_resumo_publicado_apresentado_congressos/nome_relatorio/id_trabalho_completo_resumo_publicado_apresentado_congressos/'),

    path('outra_atividade_pesquisa_producao_intelectual/<str:nome_relatorio>/', OutraAtividadePesquisaProducaoIntelectualView.as_view(), name='outra_atividade_pesquisa_producao_intelectual/nome_relatorio/'),

    path('outra_atividade_pesquisa_producao_intelectual/<str:nome_relatorio>/<int:id>/', OutraAtividadePesquisaProducaoIntelectualView.as_view(), name='outra_atividade_pesquisa_producao_intelectual/<str:nome_relatorio>/id_outra_atividade_pesquisa_producao_intelectual/'),

    path('ch_semanal_atividades_pesquisa', CHSemanalAtividadesPesquisaView.as_view(), name='ch_semanal_atividades_pesquisa'),

    path('ch_semanal_atividades_pesquisa/', CHSemanalAtividadesPesquisaView.as_view(), name='ch_semanal_atividades_pesquisa/'),

    path('ch_semanal_atividades_pesquisa/<int:id>/', CHSemanalAtividadesPesquisaView.as_view(), name='ch_semanal_atividades_pesquisa/id/'),

    path('projeto_extensao', ProjetoExtensaoView.as_view(), name='projeto_extensao'),

    path('projeto_extensao/', ProjetoExtensaoView.as_view(), name='projeto_extensao/'),

    path('projeto_extensao/<int:id>/', ProjetoExtensaoView.as_view(), name='projeto_extensao/id/'),

    path('estagio_extensao', EstagioExtensaoView.as_view(), name='estagio_extensao'),
    
    path('estagio_extensao/', EstagioExtensaoView.as_view(), name='estagio_extensao/'),

    path('estagio_extensao/<int:id>', EstagioExtensaoView.as_view(), name='estagio_extensao/id/'),

    path('atividade_ensino_nao_formal', AtividadeEnsinoNaoFormalView.as_view(), name='atividade_ensino_nao_formal'),

    path('atividade_ensino_nao_formal/', AtividadeEnsinoNaoFormalView.as_view(), name='atividade_ensino_nao_formal/'),
    
    path('atividade_ensino_nao_formal/<int:id>/', AtividadeEnsinoNaoFormalView.as_view(), name='atividade_ensino_nao_formal/id/'),

    path('outra_atividade_extensao', OutraAtividadeExtensaoView.as_view(), name='outra_atividade_extensao'),

    path('outra_atividade_extensao/', OutraAtividadeExtensaoView.as_view(), name='outra_atividade_extensao/'),

    path('outra_atividade_extensao/<int:id>/', OutraAtividadeExtensaoView.as_view(), name='outra_atividade_extensao/id/'),

    path('ch_semanal_atividades_extensao', CHSemanalAtividadesExtensaoView.as_view(), name='ch_semanal_atividades_extensao'),

    path('ch_semanal_atividades_extensao/', CHSemanalAtividadesExtensaoView.as_view(), name='ch_semanal_atividades_extensao/'),

    path('ch_semanal_atividades_extensao/<int:id>/', CHSemanalAtividadesExtensaoView.as_view(), name='ch_semanal_atividades_extensao/id/'),

    path('distribuicao_ch_semanal', DistribuicaoCHSemanalView.as_view(), name='distribuicao_ch_semanal'),

    path('distribuicao_ch_semanal/', DistribuicaoCHSemanalView.as_view(), name='distribuicao_ch_semanal/'),

    path('distribuicao_ch_semanal/<int:id>/', DistribuicaoCHSemanalView.as_view(), name='distribuicao_ch_semanal/id/'),

    path('atividade_gestao_representacao', AtividadeGestaoRepresentacaoView.as_view(), name='atividade_gestao_representacao'),

    path('atividade_gestao_representacao/', AtividadeGestaoRepresentacaoView.as_view(), name='atividade_gestao_representacao/'),

    path('atividade_gestao_representacao/<int:id>/', AtividadeGestaoRepresentacaoView.as_view(), name='atividade_gestao_representacao/id/'),
    
    path('qualificacao_docente_academica_profissional', QualificacaoDocenteAcademicaProfissionalView.as_view(), name='qualificacao_docente_academica_profissional'),
    
    path('qualificacao_docente_academica_profissional/', QualificacaoDocenteAcademicaProfissionalView.as_view(), name='qualificacao_docente_academica_profissional/'),

    path('qualificacao_docente_academica_profissional/<int:id>/', QualificacaoDocenteAcademicaProfissionalView.as_view(), name='qualificacao_docente_academica_profissional/id/'),

    path('outra_informacao', OutraInformacaoView.as_view(), name='outra_informacao'),
    
    path('outra_informacao/', OutraInformacaoView.as_view(), name='outra_informacao/'),

    path('outra_informacao/<int:id>/', OutraInformacaoView.as_view(), name='outra_informacao/id/'),

    path('afastamento', AfastamentoView.as_view(), name='afastamento'),
    
    path('afastamento/', AfastamentoView.as_view(), name='afastamento/'),

    path('afastamento/<int:id>/', AfastamentoView.as_view(), name='afastamento/id/'),

    path('documento_comprobatorio', DocumentoComprobatorioView.as_view(), name='documento_comprobatorio'),
    
    path('documento_comprobatorio/', DocumentoComprobatorioView.as_view(), name='documento_comprobatorio/'),

    path('documento_comprobatorio/<int:id>/', DocumentoComprobatorioView.as_view(), name='documento_comprobatorio/id/'),
    
    path('download_relatorio_docente/<int:relatorio_id>/', DownloadRelatorioDocenteView.as_view(), name='download_relatorio_docente/relatorio_id/'),
    
    path('extrair_dados_atividades_letivas', ExtrairDadosAtividadesLetivasPDFAPIView.as_view(), name='extrair_dados_atividades_letivas'),

    path('extrair_dados_atividades_letivas', ExtrairDadosAtividadesLetivasPDFAPIView.as_view(), name='extrair_dados_atividades_letivas'),
]