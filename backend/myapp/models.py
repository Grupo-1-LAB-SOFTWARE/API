from email.policy import default
from pyexpat import model
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models
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
        choices=REGIME,
        default='exclusivo'
    )
    titulacao = models.CharField(max_length=100)
    campus = models.CharField(max_length=150)
    instituto = models.CharField(max_length=150)

class RelatorioDocente(models.Model):
    data_criacao = models.DateField()
    ano_relatorio = models.IntegerField()
    atividades_letivas = models.JSONField()
    calculos_ch_semanal_aulas = models.JSONField()
    atividades_pedagogicas_complementares = models.JSONField()
    atividades_orientacao_supervisao_preceptoria_tutoria = models.JSONField()
    descricoes_orientacao_coorientacao_academica = models.JSONField()
    supervisoes_academicas = models.JSONField()
    preceptorias_tutorias_residencia = models.JSONField()
    bancas_examinadoras = models.JSONField()
    ch_semanal_atividade_ensino = models.JSONField()
    avaliacoes_discentes = models.JSONField()
    projetos_pesquisa_producao_intelectual = models.JSONField()
    trabalhos_completos_publicados_periodicos_boletins_tecnicos = models.JSONField()
    livros_capitulos_verbetes_publicados = models.JSONField()
    trabalhos_completos_resumos_publicados_apresentados_congressos = models.JSONField()
    outras_atividades_pesquisa_producao_intelectual = models.JSONField()
    ch_semanal_atividades_pesquisa = models.JSONField()
    projetos_extensao = models.JSONField()
    estagios_extensao = models.JSONField()
    atividades_ensino_nao_formal = models.JSONField()
    outras_atividades_extensao = models.JSONField()
    ch_semanal_atividades_extensao = models.JSONField()
    atividades_gestao_representacao = models.JSONField()
    qualificacoes_docente_academica_profissional = models.JSONField()
    distribuicao_ch_semanal = models.JSONField()
    outras_informacoes = models.JSONField()
    afastamentos = models.JSONField()


class AtividadeLetiva(models.Model):
    semestre = models.IntegerField()
    codigo_disciplina = models.CharField(max_length=20)
    nome_disciplina = models.CharField(max_length=70)
    ano_e_semestre = models.CharField(max_length=6)
    curso = models.CharField(max_length=300)
    nivel = models.CharField(max_length=250)
    numero_turmas_teorico = models.IntegerField()
    numero_turmas_pratico = models.IntegerField()
    ch_turmas_teorico = models.DecimalField(max_digits=5, decimal_places=2)
    ch_turmas_pratico = models.DecimalField(max_digits=5, decimal_places=2)
    docentes_envolvidos_e_cargas_horarias = models.JSONField()
    ch_total = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        super().clean()
        if self.ch_total > 60:
            raise ValidationError({'total': 'O valor máximo para a carga horária total é 60.'})
        if self.semestre < 0 or self.semestre > 2:
            raise ValidationError({'semestre': 'O semestre pode ser apenas 1 ou 2.'})

    class Meta:
        managed = False


class CalculoCHSemanalAulas(models.Model):
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_pos_graduacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_total = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        super().clean()
        if self.semestre < 1 or self.semestre > 2:
            raise ValidationError({'semestre': 'O semestre pode ser apenas 1 ou 2.'})

    class Meta:
        managed = False


class AtividadePedagogicaComplementar(models.Model):
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_pos_graduacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_total = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        super().clean()
        if self.semestre < 1 or self.semestre > 2:
            raise ValidationError({'semestre': 'O semestre pode ser apenas 1 ou 2.'})

    class Meta:
        managed = False


class AtividadeOrientacaoSupervisaoPreceptoriaTutoria(models.Model):
    semestre = models.IntegerField()
    ch_semanal_orientacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_coorientacao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_supervisao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_preceptoria_e_ou_tutoria = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_total = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class DescricaoOrientacaoCoorientacaoAcademica(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class SupervisaoAcademica(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class PreceptoriaTutoriaResidencia(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class BancasExaminadoras(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length=500)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class CHSemanalAtividadeEnsino(models.Model):
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class AvaliacaoDiscente(models.Model):
    numero_doc_primeiro_semestre = models.IntegerField()
    nota_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    codigo_turma_primeiro_semestre = models.CharField(max_length=50)
    numero_doc_segundo_semestre = models.IntegerField()
    nota_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    codigo_turma_segundo_semestre = models.CharField(max_length=50)

    class Meta:
        managed = False

class ProjetoPesquisaProducaoIntelectual(models.Model):
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

    class Meta:
        managed = False

class TrabalhosCompletosPeriodicosBoletinsTecnicos(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    class Meta:
        managed = False

class LivrosCapitulosVerbetesPublicados(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    class Meta:
        managed = False

class TrabalhosCompletosResumosPublicadosApresentadosCongressos(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    class Meta:
        managed = False

class OutrasAtividadesPesquisaProducaoIntelectual(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

    class Meta:
        managed = False

class CHSemanalAtividadesPesquisa(models.Model):
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class ProjetoExtensao(models.Model):
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

    class Meta:
        managed = False

class EstagioExtensao(models.Model):
    numero_doc = models.IntegerField()
    area_conhecimento = models.CharField(max_length=400)
    insituicao_ou_local = models.CharField(max_length=400)
    periodo = models.CharField(max_length=100)
    ch_semanal = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class AtividadeEnsinoNaoFormal(models.Model):
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_total_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class OutrasAtividasExtensao(models.Model):
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_total_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class CHSemanalAtividadesExtensao(models.Model):
    ch_semanal_primeiro_semestre = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_segundo_semestre = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False

class DistribuicaoCHSemanal(models.Model):
    semestre = models.IntegerField()
    ch_semanal_atividade_didatica = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_administracao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_pesquisa = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_extensao = models.DecimalField(max_digits=5, decimal_places=2)
    ch_semanal_total = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        super().clean()
        if self.ch_semanal_total > 40:
            raise ValidationError({'ch_semanal_total': 'A carga horária semanal total pode ter no máximo 40 horas'})

    class Meta:
        managed = False

class Afastamentos(models.Model):
    numero_doc = models.IntegerField()
    motivo = models.CharField(max_length = 1500)
    portaria = models.CharField(max_length= 150)

    class Meta:
        managed = False

class AtividadesGestaoRepresentacao(models.Model):
    cargo_e_ou_funcao = models.CharField(max_length=100)
    semestre = models.IntegerField()
    ch_semanal = models.DecimalField(max_digits=5, decimal_places=2)
    ato_de_designacao = models.CharField(max_length=150)
    periodo = models.CharField(max_length=100)

    class Meta:
        managed = False

class QualificacaoDocenteAcademicaProfissional(models.Model):
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)
    portaria_e_ou_data_de_realizacao = models.CharField(max_length=100)

    class Meta:
        managed = False

class OutrasInformacoes(models.Model):
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)

    class Meta:
        managed = False
