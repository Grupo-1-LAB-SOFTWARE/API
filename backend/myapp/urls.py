from django.urls import path

from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    RelatorioDocenteAdminView, RelatorioDocenteView, AtividadeLetivaView, CalculoCHSemanalAulasView, AtividadePedagogicaComplementarView, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView, DescricaoOrientacaoCoorientacaoAcademicaView, SupervisaoAcademicaView, PreceptoriaTutoriaResidenciaView, BancaExaminadoraView, CHSemanalAtividadeEnsinoView, AvaliacaoDiscenteView, ProjetoPesquisaProducaoIntelectualView, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView, LivroCapituloVerbetePublicadoView, TrabalhoCompletoResumoPublicadoApresentadoCongressosView, OutraAtividadePesquisaProducaoIntelectualView, CHSemanalAtividadesPesquisaView, ProjetoExtensaoView, EstagioExtensaoView, AtividadeEnsinoNaoFormalView, OutraAtividadeExtensaoView, CHSemanalAtividadesExtensaoView, DistribuicaoCHSemanalView, AtividadeGestaoRepresentacaoView, QualificacaoDocenteAcademicaProfissionalView, OutraInformacaoView, AfastamentoView, DocumentoComprobatorioView, DownloadRelatorioDocenteView, CriarUsuarioView, ExtrairDadosAtividadesLetivasPDFAPIView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    
    path('usuarios', UsuarioView.as_view(), name='usuarios'),

    path('usuarios/', UsuarioView.as_view(), name='usuarios/'),

    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios/id/'),

    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),

    path('login', LoginView.as_view(), name='login'),

    path('login/', LoginView.as_view(), name='login/'),

    path('atividade_letiva', AtividadeLetivaView.as_view(), name='atividade_letiva'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva/'),

    path('atividade_letiva/<int:id>/', AtividadeLetivaView.as_view(), name='atividade_letiva/id/'),

    path('atividade_letiva/', AtividadeLetivaView.as_view(), name='atividade_letiva/'),

    path('relatorio_docente/admin', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin'),

    path('relatorio_docente/admin/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/'),

    path('relatorio_docente/admin/<int:id>/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/id/'),

    path('relatorio_docente/admin/usuario/<int:user_id>/', RelatorioDocenteAdminView.as_view(), name='relatorio_docente/admin/usuario/id/'),

    path('relatorio_docente', RelatorioDocenteView.as_view(), name='relatorio_docente'),

    path('relatorio_docente/', RelatorioDocenteView.as_view(), name='relatorio_docente/'),

    path('relatorio_docente/<str:nome>/', RelatorioDocenteView.as_view(), name='relatorio_docente/nome/'),

    path('calculo_ch_semanal_aulas/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas/'),

    path('calculo_ch_semanal_aulas', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas'),

    path('calculo_ch_semanal_aulas/<int:id>/', CalculoCHSemanalAulasView.as_view(), name='calculo_ch_semanal_aulas/id/'),

    path('atividade_pedagogica_complementar', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar'),

    path('atividade_pedagogica_complementar/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/'),

    path('atividade_pedagogica_complementar/<int:id>/', AtividadePedagogicaComplementarView.as_view(), name='atividade_pedagogica_complementar/id/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/'),

    path('atividade_orientacao_supervisao_preceptoria_tutoria/<int:id>/', AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView.as_view(), name='atividade_orientacao_supervisao_preceptoria_tutoria/id/'),

    path('descricao_orientacao_coorientacao_academica', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica'),

    path('descricao_orientacao_coorientacao_academica/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/'),

    path('descricao_orientacao_coorientacao_academica/<int:id>/', DescricaoOrientacaoCoorientacaoAcademicaView.as_view(), name='descricao_orientacao_coorientacao_academica/id/'),

    path('supervisao_academica', SupervisaoAcademicaView.as_view(), name='supervisao_academica'),
    
    path('supervisao_academica/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/'),

    path('supervisao_academica/<int:id>/', SupervisaoAcademicaView.as_view(), name='supervisao_academica/id//'),

    path('preceptoria_tutoria_residencia', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia'),

    path('preceptoria_tutoria_residencia/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/'),

    path('preceptoria_tutoria_residencia/<int:id>/', PreceptoriaTutoriaResidenciaView.as_view(), name='preceptoria_tutoria_residencia/id/'),

    path('banca_examinadora', BancaExaminadoraView.as_view(), name='banca_examinadora'),

    path('banca_examinadora/', BancaExaminadoraView.as_view(), name='banca_examinadora/'),

    path('banca_examinadora/<int:id>/', BancaExaminadoraView.as_view(), name='banca_examinadora/id/'),

    path('ch_semanal_atividades_ensino', CHSemanalAtividadeEnsinoView.as_view(), name='ch_semanal_atividades_ensino'),

    path('ch_semanal_atividades_ensino/', CHSemanalAtividadeEnsinoView.as_view(), name='ch_semanal_atividades_ensino/'),

    path('ch_semanal_atividades_ensino/<int:id>/', CHSemanalAtividadeEnsinoView.as_view(), name='ch_semanal_atividades_ensino/id/'),

    path('avaliacao_discente', AvaliacaoDiscenteView.as_view(), name='avaliacao_discente'),

    path('avaliacao_discente/', AvaliacaoDiscenteView.as_view(), name='avaliacao_discente/'),

    path('avaliacao_discente/<int:id>/', AvaliacaoDiscenteView.as_view(), name='avaliacao_discente/id/'),

    path('projeto_pesquisa_producao_intelectual', ProjetoPesquisaProducaoIntelectualView.as_view(), name='projeto_pesquisa_producao_intelectual'),
    
    path('projeto_pesquisa_producao_intelectual/', ProjetoPesquisaProducaoIntelectualView.as_view(), name='projeto_pesquisa_producao_intelectual/'),

    path('projeto_pesquisa_producao_intelectual/<int:id>/', ProjetoPesquisaProducaoIntelectualView.as_view(), name='projeto_pesquisa_producao_intelectual/id'),

    path('trabalho_completo_publicado_periodico_boletim_tecnico', TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView.as_view(), name='trabalho_completo_publicado_periodico_boletim_tecnico'),

    path('trabalho_completo_publicado_periodico_boletim_tecnico/', TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView.as_view(), name='trabalho_completo_publicado_periodico_boletim_tecnico/'),

    path('trabalho_completo_publicado_periodico_boletim_tecnico/<int:id>', TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView.as_view(), name='trabalho_completo_publicado_periodico_boletim_tecnico/id/'),

    path('livro_capitulo_verbete_publicado', LivroCapituloVerbetePublicadoView.as_view(), name='livro_capitulo_verbete_publicado'),

    path('livro_capitulo_verbete_publicado/', LivroCapituloVerbetePublicadoView.as_view(), name='livro_capitulo_verbete_publicado/'),

    path('livro_capitulo_verbete_publicado/<int:id>/', LivroCapituloVerbetePublicadoView.as_view(), name='livro_capitulo_verbete_publicado/id/'),

    path('trabalho_completo_resumo_publicado_apresentado_congressos', TrabalhoCompletoResumoPublicadoApresentadoCongressosView.as_view(), name='trabalho_completo_resumo_publicado_apresentado_congressos'),

    path('trabalho_completo_resumo_publicado_apresentado_congressos/', TrabalhoCompletoResumoPublicadoApresentadoCongressosView.as_view(), name='trabalho_completo_resumo_publicado_apresentado_congressos/'),

    path('trabalho_completo_resumo_publicado_apresentado_congressos/<int:id>/', TrabalhoCompletoResumoPublicadoApresentadoCongressosView.as_view(), name='trabalho_completo_resumo_publicado_apresentado_congressos/id/'),

    path('outra_atividade_pesquisa_producao_intelectual', OutraAtividadePesquisaProducaoIntelectualView.as_view(), name='outra_atividade_pesquisa_producao_intelectual'),

    path('outra_atividade_pesquisa_producao_intelectual/', OutraAtividadePesquisaProducaoIntelectualView.as_view(), name='outra_atividade_pesquisa_producao_intelectual/'),

    path('outra_atividade_pesquisa_producao_intelectual/<int:id>/', OutraAtividadePesquisaProducaoIntelectualView.as_view(), name='outra_atividade_pesquisa_producao_intelectual/id/'),

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

    path('criar_usuario', CriarUsuarioView.as_view(), name='criar_usuario'),
    
    path('criar_usuario/', CriarUsuarioView.as_view(), name='criar_usuario/'),

    path('criar_usuario/<int:id>/', CriarUsuarioView.as_view(), name='criar_usuario/id/'),
    
    path('download_relatorio_docente/<int:relatorio_id>/', DownloadRelatorioDocenteView.as_view(), name='download_relatorio_docente/relatorio_id/'),
    
    path('extrair_dados_atividades_letivas', ExtrairDadosAtividadesLetivasPDFAPIView.as_view(), name='extrair_dados_atividades_letivas'),

    path('extrair_dados_atividades_letivas', ExtrairDadosAtividadesLetivasPDFAPIView.as_view(), name='extrair_dados_atividades_letivas'),
]