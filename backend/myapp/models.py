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

class AtividadeLetiva(models.Model):
    codigo_disciplina = models.CharField(max_length=10)
    nome_disciplina = models.CharField(max_length=70)
    ano = models.CharField(max_length=4)
    semestre = models.IntegerField()
    curso = models.CharField(max_length=300)
    nivel = models.CharField(max_length=250)
    numero_turmas_teorico = models.IntegerField()
    numero_turmas_pratico = models.IntegerField()
    ch_turmas_teorico = models.DecimalField()
    ch_turmas_pratico = models.DecimalField()
    docentes_envolvidos_e_cargas_horarias = models.JSONField()
    ch_total = models.DecimalField(default= (numero_turmas_teorico * ch_turmas_teorico) + (numero_turmas_pratico * ch_turmas_pratico))

    def clean(self):
        super().clean()
        if self.ch_total > 60:
            raise ValidationError({'total': 'O valor máximo para a carga horária total é 60.'})

class CHSemanalAulas(models.Model):
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.DecimalField()
    ch_semanal_pos_graduacao = models.DecimalField()
    ch_semanal_total = models.DecimalField(default= ch_semanal_graduacao + ch_semanal_pos_graduacao)

    def clean(self):
        super().clean()
        if self.semestre < 1 or self.semestre > 2:
            raise ValidationError({'semestre': 'O semestre pode ser apenas 1 ou 2.'})


class AtividadePedagogicaComplementar(models.Model):
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.DecimalField()
    ch_semanal_pos_graduacao = models.DecimalField()
    ch_semanal_total = models.DecimalField(default= ch_semanal_graduacao + ch_semanal_pos_graduacao)

    def clean(self):
        super().clean()
        if self.semestre < 1 or self.semestre > 2:
            raise ValidationError({'semestre': 'O semestre pode ser apenas 1 ou 2.'})


class AtividadeOrientacao(models.Model):
    semestre = models.IntegerField()
    ch_semanal_orientacao = models.DecimalField()
    ch_semanal_coorientacao = models.DecimalField()
    ch_semanal_supervisao = models.DecimalField()
    ch_semanal_preceptoria_e_ou_tutoria = models.DecimalField()
    ch_semanal_total = models.DecimalField(default= ch_semanal_orientacao + ch_semanal_coorientacao + ch_semanal_preceptoria_e_ou_tutoria + ch_semanal_supervisao)

class DescricaoOrientacaoCoorientacaoAcademica(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class SupervisaoAcademica(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class PreceptoriaTutoriaResidencia(models.Model):
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class BancasExaminadoras(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length=500)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class CHSemanalAtividadeEnsino(models.Model):
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class AvaliacaoDiscente(models.Model):
    numero_doc_primeiro_semestre = models.IntegerField()
    nota_primeiro_semestre = models.DecimalField()
    codigo_turma_primeiro_semestre = models.CharField(max_length=50)
    numero_doc_segundo_semestre = models.IntegerField()
    nota_segundo_semestre = models.DecimalField()
    codigo_turma_segundo_semestre = models.CharField(max_length=50)

class ProjetoPesquisaProducao(models.Model):
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
        max_length=10,
        choices=FUNCAO,
        default='coordenador'
    )
    cadastro_proped = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='concluida'
    )

class TrabalhosCompletosPeriodicosBoletins(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class LivrosCapitulosVerbetes(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class TrabalhosCompletosResumos(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class OutrasAtividadesPesquisaProducao(models.Model):
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class CHSemanalAtividadesPesquisa(models.Model):
    ch_semanal_primeiro_semestre = models.DecimalField()
    ch_semanal_segundo_semestre = models.DecimalField()

class ProjetosExtensao(models.Model):
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
        max_length=10,
        choices=FUNCAO,
        default='coordenador'
    )
    cadastro_proex = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='concluida'
    )


class RelatorioDocente(models.Model):
    data_criacao = models.DateField()
    ano_relatorio = models.IntegerField()