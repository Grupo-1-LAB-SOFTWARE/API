from email.policy import default
from pyexpat import model
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
    
class Usuario(AbstractUser):
    CLASSE = (
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
    )
    REGIME = (
        ('exclusivo', 'Dedicação Exclusiva'),
        ('integral', '40h'),
        ('parcial', '20h'),
    )
    VINCULO = (
        ('estatuario', 'Estatuário'),
        ('não selecionado', 'Não selecionado')
    )
    TITULACAO = (
        ('graduacao', 'Graduação'),
        ('especializacao', 'Especialização'),
        ('mestre', 'Mestre'),
        ('doutor', 'Doutor'),
    )
    PERFIL = (
        ('docente', 'Docente'),
        ('admin', 'Administrador'),
    )
    id = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=500)
    perfil = models.CharField(
        max_length=10,
        choices=PERFIL,
        default='docente'
    )
    email = models.EmailField(unique=True)
    siape = models.CharField(max_length=500)
    classe = models.CharField(
        max_length=30,
        choices=CLASSE,
        default='a'
    )
    vinculo = models.CharField(
        max_length=100,
        choices=VINCULO
    )
    regime_de_trabalho = models.CharField(
        max_length=50,
        choices=REGIME
    )
    titulacao = models.CharField(
        max_length=100,
        choices=TITULACAO
    )
    campus = models.CharField(max_length=150)
    instituto = models.CharField(max_length=150)
    confirmar_email = models.EmailField(null=True)
    confirmar_senha = models.CharField(max_length=128, null=True)

class RelatorioDocente(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(Usuario, related_name="usuario_id", on_delete=models.CASCADE)
    data_criacao = models.DateField()
    ano_relatorio = models.CharField(max_length=4)
    atividades_letivas = models.JSONField(null=True)
    calculos_ch_semanal_aulas = models.JSONField(null=True)
    atividades_pedagogicas_complementares = models.JSONField(null=True)
    atividades_orientacao_supervisao_preceptoria_tutoria = models.JSONField(null=True)
    descricoes_orientacao_coorientacao_academica = models.JSONField(null=True)
    supervisoes_academicas = models.JSONField(null=True)
    preceptorias_tutorias_residencia = models.JSONField(null=True)
    bancas_examinadoras = models.JSONField(null=True)
    ch_semanal_atividade_ensino = models.JSONField(null=True)
    avaliacoes_discentes = models.JSONField(null=True)
    projetos_pesquisa_producao_intelectual = models.JSONField(null=True)
    trabalhos_completos_publicados_periodicos_boletins_tecnicos = models.JSONField(null=True)
    livros_capitulos_verbetes_publicados = models.JSONField(null=True)
    trabalhos_completos_resumos_publicados_apresentados_congressos = models.JSONField(null=True)
    outras_atividades_pesquisa_producao_intelectual = models.JSONField(null=True)
    ch_semanal_atividades_pesquisa = models.JSONField(null=True)
    projetos_extensao = models.JSONField(null=True)
    estagios_extensao = models.JSONField(null=True)
    atividades_ensino_nao_formal = models.JSONField(null=True)
    outras_atividades_extensao = models.JSONField(null=True)
    ch_semanal_atividades_extensao = models.JSONField(null=True)
    atividades_gestao_representacao = models.JSONField(null=True)
    qualificacoes_docente_academica_profissional = models.JSONField(null=True)
    distribuicao_ch_semanal = models.JSONField(null=True)
    outras_informacoes = models.JSONField(null=True)
    afastamentos_json = models.JSONField(null=True)

    def atualizar_atividades_letivas(self):
        atividades_letivas_letivas = list(self.atividadeletiva_set.all().values())
        self.atividades_letivas = atividades_letivas_letivas
        self.save()

    def atualizar_calculos_ch_semanal_aulas(self):
        calculos_ch_semanal_aulas = list(self.calculochsemanalaulas_set.all().values())
        self.calculos_ch_semanal_aulas = calculos_ch_semanal_aulas
        self.save()

    def atualizar_atividades_pedagogicas_complementares(self):
        atividades_pedagogicas_complementares = list(self.atividadepedagogicacomplementar_set.all().values())
        self.atividades_pedagogicas_complementares = atividades_pedagogicas_complementares
        self.save()

    def atualizar_atividades_orientacao_supervisao_preceptoria_tutoria(self):
        atividades_orientacao_supervisao_preceptoria_tutoria = list(self.atividadeorientacaosupervisaopreceptoriatutoria_set.all().values())
        self.atividades_orientacao_supervisao_preceptoria_tutoria = atividades_orientacao_supervisao_preceptoria_tutoria
        self.save()

    def atualizar_descricoes_orientacao_coorientacao_academica(self):
        descricoes_orientacao_coorientacao_academica = list(self.descricaoorientacaocoorientacaoacademica_set.all().values())
        self.descricoes_orientacao_coorientacao_academica = descricoes_orientacao_coorientacao_academica
        self.save()

    def atualizar_atualizar_supervisoes_academicas(self):
        supervisoes_academicas = list(self.supervisoesacademicas_set.all().values())
        self.supervisoes_academicas = supervisoes_academicas
        self.save()
    
    def atualizar_preceptorias_tutorias_residencia(self):
        preceptorias_tutorias_residencia = list(self.preceptoriastutoriasresidencia_set.all().values())
        self.preceptorias_tutorias_residencia = preceptorias_tutorias_residencia
        self.save()
    
    def atualizar_bancas_examinadoras(self):
        bancas_examinadoras = list(self.bancasexaminadoras_set.all().values())
        self.bancas_examinadoras = bancas_examinadoras
        self.save()

    def atualizar_ch_semanal_atividade_ensino(self):
        ch_semanal_atividade_ensino = list(self.chsemanalatividadeensino_set.all().values())
        self.ch_semanal_atividade_ensino = ch_semanal_atividade_ensino
        self.save()

    def atualizar_avaliacoes_discentes(self):
        avaliacoes_discentes = list(self.avaliacoesdiscentes_set.all().values())
        self.avaliacoes_discentes = avaliacoes_discentes
        self.save()

    def atualizar_projetos_pesquisa_producao_intelectual(self):
        projetos_pesquisa_producao_intelectual = list(self.projetospesquisaproducaointelectual_set.all().values())
        self.projetos_pesquisa_producao_intelectual = projetos_pesquisa_producao_intelectual
        self.save()

    def atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos(self):
        trabalhos_completos_publicados_periodicos_boletins_tecnicos = list(self.trabalhoscompletospublicadosperiodicosboletinstecnicos_set.all().values())
        self.trabalhos_completos_publicados_periodicos_boletins_tecnicos = trabalhos_completos_publicados_periodicos_boletins_tecnicos
        self.save()   

    def atualizar_livros_capitulos_verbetes_publicados(self):
        livros_capitulos_verbetes_publicados = list(self.livroscapitulosverbetespublicadosl_set.all().values())
        self.livros_capitulos_verbetes_publicados = livros_capitulos_verbetes_publicados
        self.save()

    def atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos(self):
        trabalhos_completos_resumos_publicados_apresentados_congressos = list(self.trabalhoscompletosresumospublicadosapresentadoscongressos_set.all().values())
        self.trabalhos_completos_resumos_publicados_apresentados_congressos = trabalhos_completos_resumos_publicados_apresentados_congressos
        self.save()

    def atualizar_outras_atividades_pesquisa_producao_intelectual(self):
        outras_atividades_pesquisa_producao_intelectual = list(self.outrasatividadespesquisaproducaointelectual_set.all().values())
        self.outras_atividades_pesquisa_producao_intelectual = outras_atividades_pesquisa_producao_intelectual
        self.save()

    def atualizar_ch_semanal_atividades_pesquisa(self):
        ch_semanal_atividades_pesquisa = list(self.chsemanalatividadespesquisa_set.all().values())
        self.ch_semanal_atividades_pesquisa = ch_semanal_atividades_pesquisa
        self.save()

    def atualizar_projetos_extensao(self):
        projetos_extensao = list(self.projetosextensao_set.all().values())
        self.projetos_extensao = projetos_extensao
        self.save()

    def atualizar_estagios_extensao(self):
        estagios_extensao = list(self.estagiosextensao_set.all().values())
        self.estagios_extensao = estagios_extensao
        self.save()

    def atualizar_atividades_ensino_nao_formal(self):
        atividades_ensino_nao_formal = list(self.atividadesensinonaoformal_set.all().values())
        self.atividades_ensino_nao_formal = atividades_ensino_nao_formal
        self.save()

    def atualizar_outras_atividades_extensao(self):
        outras_atividades_extensao = list(self.outrasatividadesextensao_set.all().values())
        self.outras_atividades_extensao = outras_atividades_extensao
        self.save()

    def atualizar_ch_semanal_atividades_extensao(self):
        ch_semanal_atividades_extensao = list(self.chsemanalatividadesextensao_set.all().values())
        self.ch_semanal_atividades_extensao = ch_semanal_atividades_extensao
        self.save()

    def atualizar_atividades_gestao_representacao(self):
        atividades_gestao_representacao = list(self.atividadesgestaorepresentacao_set.all().values())
        self.atividades_gestao_representacao = atividades_gestao_representacao
        self.save()
    
    def atualizar_qualificacoes_docente_academica_profissional(self):
        qualificacoes_docente_academica_profissional = list(self.qualificacoesdocenteacademicaprofissional_set.all().values())
        self.qualificacoes_docente_academica_profissional = qualificacoes_docente_academica_profissional
        self.save()

    def atualizar_distribuicao_ch_semanal(self):
        distribuicao_ch_semanal = list(self.distribuicaochsemanal_set.all().values())
        self.distribuicao_ch_semanal = distribuicao_ch_semanal
        self.save()

    def atualizar_outras_informacoes(self):
        outras_informacoes = list(self.outrasinformacoes_set.all().values())
        self.outras_informacoes = outras_informacoes
        self.save()

    def atualizar_afastamentos(self):
        afastamentos_json = list(self.afastamentosjson_set.all().values())
        self.afastamentos_json = afastamentos_json
        self.save()

class AtividadeLetiva(models.Model):
    relatorio_id_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    codigo_disciplina = models.CharField(max_length=20)
    nome_disciplina = models.CharField(max_length=70)
    ano_e_semestre = models.CharField(max_length=6)
    curso = models.CharField(max_length=300)
    nivel = models.CharField(max_length=250)
    numero_turmas_teorico = models.IntegerField()
    numero_turmas_pratico = models.IntegerField()
    ch_turmas_teorico = models.FloatField()
    ch_turmas_pratico = models.FloatField()
    docentes_envolvidos_e_cargas_horarias = models.JSONField()
    ch_total = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id_id.atualizar_atividades_letivas()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id_id.atualizar_atividades_letivas()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_letivas()

class CalculoCHSemanalAulas(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.FloatField()
    ch_semanal_pos_graduacao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_calculos_ch_semanal_aulas()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_calculos_ch_semanal_aulas()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_calculos_ch_semanal_aulas()


class AtividadePedagogicaComplementar(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.FloatField()
    ch_semanal_pos_graduacao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_pedagogicas_complementares()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_pedagogicas_complementares()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_pedagogicas_complementares()


class AtividadeOrientacaoSupervisaoPreceptoriaTutoria(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_orientacao = models.FloatField()
    ch_semanal_coorientacao = models.FloatField()
    ch_semanal_supervisao = models.FloatField()
    ch_semanal_preceptoria_e_ou_tutoria = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_orientacao_supervisao_preceptoria_tutoria()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_orientacao_supervisao_preceptoria_tutoria()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_orientacao_supervisao_preceptoria_tutoria()


class DescricaoOrientacaoCoorientacaoAcademica(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_descricoes_orientacao_coorientacao_academica()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_descricoes_orientacao_coorientacao_academica()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_descricoes_orientacao_coorientacao_academica()


class SupervisaoAcademica(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_supervisoes_academicas()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_supervisoes_academicas()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_supervisoes_academicas()

class PreceptoriaTutoriaResidencia(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_preceptorias_tutorias_residencia()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_preceptorias_tutorias_residencia()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_preceptorias_tutorias_residencia()

class BancasExaminadoras(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_candidato = models.CharField(max_length=400)
    titulo_trabalho = models.CharField(max_length=500)
    ies = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_bancas_examinadoras()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_bancas_examinadoras()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_bancas_examinadoras()

class CHSemanalAtividadeEnsino(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividade_ensino()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividade_ensino()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividade_ensino()

class AvaliacaoDiscente(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc_primeiro_semestre = models.IntegerField()
    nota_primeiro_semestre = models.FloatField()
    codigo_turma_primeiro_semestre = models.CharField(max_length=50)
    numero_doc_segundo_semestre = models.IntegerField()
    nota_segundo_semestre = models.FloatField()
    codigo_turma_segundo_semestre = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_avaliacoes_discentes()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_avaliacoes_discentes()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_avaliacoes_discentes()

class ProjetoPesquisaProducaoIntelectual(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    FUNCAO = (
        ('coordenador', 'Coordenador'),
        ('colaborador', 'Colaborador'),
    )
    SITUACAO_ATUAL = (
        ('concluida', 'CONCLUÍDA'),
        ('em_andamento', 'EM ANDAMENTO'),
        ('em_pausa', 'EM PAUSA'),
    )

    numero_doc = models.IntegerField()
    titulo = models.CharField(max_length=600)
    funcao = models.CharField(
        max_length=20,
        choices=FUNCAO,
        default='coordenador'
    )
    cadastro_proped = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='concluida'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_pesquisa_producao_intelectual()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_pesquisa_producao_intelectual()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_pesquisa_producao_intelectual()

class TrabalhosCompletosPeriodicosBoletinsTecnicos(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos()

class LivrosCapitulosVerbetesPublicados(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_livros_capitulos_verbetes_publicados()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_livros_capitulos_verbetes_publicados()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_livros_capitulos_verbetes_publicados()

class TrabalhosCompletosResumosPublicadosApresentadosCongressos(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos()

class OutrasAtividadesPesquisaProducaoIntelectual(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_pesquisa_producao_intelectual()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_pesquisa_producao_intelectual()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_pesquisa_producao_intelectual()


class CHSemanalAtividadesPesquisa(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_pesquisa()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_pesquisa()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_pesquisa()

class ProjetoExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    FUNCAO = (
        ('coordenador', 'Coordenador'),
        ('colaborador', 'Colaborador'),
    )
    SITUACAO_ATUAL = (
        ('concluida', 'CONCLUÍDA'),
        ('em_andamento', 'EM ANDAMENTO'),
        ('em_pausa', 'EM PAUSA'),
    )

    numero_doc = models.IntegerField()
    titulo = models.CharField(max_length=600)
    funcao = models.CharField(
        max_length=20,
        choices=FUNCAO,
        default='coordenador'
    )
    cadastro_proex = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='concluida'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_extensao()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_extensao()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_projetos_extensao()

class EstagioExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    area_conhecimento = models.CharField(max_length=400)
    insituicao_ou_local = models.CharField(max_length=400)
    periodo = models.CharField(max_length=100)
    ch_semanal = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_estagios_extensao()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_estagios_extensao()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_estagios_extensao()

class AtividadeEnsinoNaoFormal(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.FloatField()
    ch_semanal_primeiro_semestre = models.FloatField(null=True)
    ch_total_segundo_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField(null=True)

    def save(self):
        self.ch_semanal_primeiro_semestre = float(self.ch_total_primeiro_semestre) / 23
        self.ch_semanal_segundo_semestre = float(self.ch_semanal_segundo_semestre) / 23
        super().save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_ensino_nao_formal()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_ensino_nao_formal()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_ensino_nao_formal()

class OutrasAtividasExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.FloatField()
    ch_semanal_primeiro_semestre = models.FloatField(null=True)
    ch_total_segundo_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField(null=True)

    def save(self):
        self.ch_semanal_primeiro_semestre = float(self.ch_total_primeiro_semestre) / 23
        self.ch_semanal_segundo_semestre = float(self.ch_semanal_segundo_semestre) / 23
        super().save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_extensao()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_extensao()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_outras_atividades_extensao()

class CHSemanalAtividadesExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_extensao()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_extensao()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_ch_semanal_atividades_extensao()

class DistribuicaoCHSemanal(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_atividade_didatica = models.FloatField()
    ch_semanal_administracao = models.FloatField()
    ch_semanal_pesquisa = models.FloatField()
    ch_semanal_extensao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

    def save(self):
        self.ch_semanal_total = float(self.ch_semanal_atividade_didatica) + float(self.ch_semanal_administracao) + float(self.ch_semanal_pesquisa) + float(self.ch_semanal_extensao)
        super().save()

    def clean(self):
        super().clean()
        if self.ch_semanal_total > 40:
            raise ValidationError({'ch_semanal_total': 'A carga horária semanal total pode ter no máximo 40 horas'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_distribuicao_ch_semanal()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_distribuicao_ch_semanal()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_distribuicao_ch_semanal()

class Afastamentos(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    motivo = models.CharField(max_length = 1500)
    portaria = models.CharField(max_length= 150)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_afastamentos()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_afastamentos()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_afastamentos()

class AtividadesGestaoRepresentacao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    cargo_e_ou_funcao = models.CharField(max_length=100)
    semestre = models.IntegerField()
    ch_semanal = models.FloatField()
    ato_de_designacao = models.CharField(max_length=150)
    periodo = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_gestao_representacao()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_gestao_representacao()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_atividades_gestao_representacao()

class QualificacaoDocenteAcademicaProfissional(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)
    portaria_e_ou_data_de_realizacao = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_qualificacoes_docente_academica_profissional()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_qualificacoes_docente_academica_profissional()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_qualificacoes_docente_academica_profissional()

class OutrasInformacoes(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.relatorio_id.atualizar_outras_informacoes()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.relatorio_id.atualizar_outras_informacoes()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.relatorio_id.atualizar_outras_informacoes()


@receiver(post_save, sender=AtividadeLetiva)
def atualizar_atividades_letivas(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atividades_letivas()

@receiver(post_save, sender=CalculoCHSemanalAulas)
def atualizar_calculos_ch_semanal_aulas(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_calculos_ch_semanal_aulas()

@receiver(post_save, sender=AtividadePedagogicaComplementar)
def atualizar_atividades_pedagogicas_complementares(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atividades_pedagogicas_complementares()

@receiver(post_save, sender=AtividadeOrientacaoSupervisaoPreceptoriaTutoria)
def atualizar_atividades_orientacao_supervisao_preceptoria_tutoria(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atividades_orientacao_supervisao_preceptoria_tutoria()

@receiver(post_save, sender=DescricaoOrientacaoCoorientacaoAcademica)
def atualizar_descricoes_orientacao_coorientacao_academica(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_descricoes_orientacao_coorientacao_academica()

@receiver(post_save, sender=SupervisaoAcademica)
def atualizar_atualizar_supervisoes_academicas(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atualizar_supervisoes_academicas()

@receiver(post_save, sender=PreceptoriaTutoriaResidencia)
def atualizar_preceptorias_tutorias_residencia(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_preceptorias_tutorias_residencia()

@receiver(post_save, sender=BancasExaminadoras)
def atualizar_bancas_examinadoras(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_bancas_examinadoras()

@receiver(post_save, sender=CHSemanalAtividadeEnsino)
def atualizar_ch_semanal_atividade_ensino(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_ch_semanal_atividade_ensino()

@receiver(post_save, sender=AvaliacaoDiscente)
def atualizar_avaliacoes_discentes(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_avaliacoes_discentes()

@receiver(post_save, sender=ProjetoPesquisaProducaoIntelectual)
def atualizar_projetos_pesquisa_producao_intelectual(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_projetos_pesquisa_producao_intelectual()

@receiver(post_save, sender=TrabalhosCompletosPeriodicosBoletinsTecnicos)
def atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_trabalhos_completos_publicados_periodicos_boletins_tecnicos()

@receiver(post_save, sender=LivrosCapitulosVerbetesPublicados)
def atualizar_livros_capitulos_verbetes_publicados(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_livros_capitulos_verbetes_publicados()

@receiver(post_save, sender=TrabalhosCompletosResumosPublicadosApresentadosCongressos)
def atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_trabalhos_completos_resumos_publicados_apresentados_congressos()

@receiver(post_save, sender=OutrasAtividadesPesquisaProducaoIntelectual)
def atualizar_outras_atividades_pesquisa_producao_intelectual(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_outras_atividades_pesquisa_producao_intelectual()

@receiver(post_save, sender=CHSemanalAtividadesPesquisa)
def atualizar_ch_semanal_atividades_pesquisa(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_ch_semanal_atividades_pesquisa()

@receiver(post_save, sender=ProjetoExtensao)
def atualizar_projetos_extensao(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_projetos_extensao()

@receiver(post_save, sender=EstagioExtensao)
def atualizar_estagios_extensao(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_estagios_extensao()

@receiver(post_save, sender=AtividadeEnsinoNaoFormal)
def atualizar_atividades_ensino_nao_formal(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atividades_ensino_nao_formal()

@receiver(post_save, sender=OutrasAtividasExtensao)
def atualizar_outras_atividades_extensao(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_outras_atividades_extensao()

@receiver(post_save, sender=CHSemanalAtividadesExtensao)
def atualizar_ch_semanal_atividades_extensao(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_ch_semanal_atividades_extensao()

@receiver(post_save, sender=AtividadesGestaoRepresentacao)
def atualizar_atividades_gestao_representacao(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_atividades_gestao_representacao()

@receiver(post_save, sender=QualificacaoDocenteAcademicaProfissional)
def atualizar_qualificacoes_docente_academica_profissional(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_qualificacoes_docente_academica_profissional()

@receiver(post_save, sender=DistribuicaoCHSemanal)
def atualizar_distribuicao_ch_semanal(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_distribuicao_ch_semanal()

@receiver(post_save, sender=OutrasInformacoes)
def atualizar_outras_informacoes(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_outras_informacoes()

@receiver(post_save, sender=Afastamentos)
def atualizar_afastamentos(sender, instance, **kwargs):
    instance.relatorio_id.atualizar_afastamentos()
