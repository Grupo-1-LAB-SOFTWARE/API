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
        ('Exclusivo', 'Dedicação Exclusiva'),
        ('Integral', 'Integral'),
        ('Parcial', 'Parcial'),
    )
    VINCULO = (
        ('Estatuário', 'Estatuário'),
        ('Não selecionado', 'Não selecionado')
    )
    TITULACAO = (
        ('Graduação', 'Graduação'),
        ('Especialização', 'Especialização'),
        ('Mestre', 'Mestre'),
        ('Doutor', 'Doutor'),
    )
    PERFIL = (
        ('Docente', 'Docente'),
        ('Administrador', 'Administrador'),
    )
    id = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=500)
    perfil = models.CharField(
        max_length=50,
        choices=PERFIL,
        default='Docente'
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
    nome = models.CharField(max_length = 50)
    usuario_id = models.ForeignKey(Usuario, related_name="usuario_id", on_delete=models.CASCADE)
    data_criacao = models.DateField()
    ano_relatorio = models.CharField(max_length=4)

class AtividadeLetiva(models.Model):
    NIVEL = (
        ('GRA', 'GRA'),
        ('POS', 'POS'),
        ('MES', 'MES'),
        ('DOC', 'DOC'),
    )
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    codigo_disciplina = models.CharField(max_length=20)
    nome_disciplina = models.CharField(max_length=70)
    ano_e_semestre = models.CharField(max_length=6)
    curso = models.CharField(max_length=300)
    nivel = models.CharField(
        max_length=10,
        choices=NIVEL,
        default='GRA'
    )
    numero_turmas_teorico = models.IntegerField()
    numero_turmas_pratico = models.IntegerField()
    ch_turmas_teorico = models.FloatField()
    ch_turmas_pratico = models.FloatField()
    docentes_envolvidos_e_cargas_horarias = models.JSONField()
    ch_total = models.FloatField(null=True)

class CalculoCHSemanalAulas(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.FloatField()
    ch_semanal_pos_graduacao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

class AtividadePedagogicaComplementar(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_graduacao = models.FloatField()
    ch_semanal_pos_graduacao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

class AtividadeOrientacaoSupervisaoPreceptoriaTutoria(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_orientacao = models.FloatField()
    ch_semanal_coorientacao = models.FloatField()
    ch_semanal_supervisao = models.FloatField()
    ch_semanal_preceptoria_e_ou_tutoria = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

class DescricaoOrientacaoCoorientacaoAcademica(models.Model):
    NIVEL = (
        ('GRA', 'GRA'),
        ('POS', 'POS'),
        ('MES', 'MES'),
        ('DOC', 'DOC'),
    )
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(
        max_length=50,
        choices=NIVEL,
        default='GRA'
    )
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class SupervisaoAcademica(models.Model):
    NIVEL = (
        ('GRA', 'GRA'),
        ('POS', 'POS'),
        ('MES', 'MES'),
        ('DOC', 'DOC'),
    )
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    curso = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(
        max_length=50,
        choices=NIVEL,
        default='GRA'
    )
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class PreceptoriaTutoriaResidencia(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_e_ou_matricula_discente = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class BancaExaminadora(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    nome_candidato = models.CharField(max_length=400)
    titulo_trabalho = models.CharField(max_length=500)
    ies = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class CHSemanalAtividadeEnsino(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE, unique=True)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class AvaliacaoDiscente(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc_primeiro_semestre = models.IntegerField()
    nota_primeiro_semestre = models.FloatField()
    codigo_turma_primeiro_semestre = models.CharField(max_length=50)
    numero_doc_segundo_semestre = models.IntegerField()
    nota_segundo_semestre = models.FloatField()
    codigo_turma_segundo_semestre = models.CharField(max_length=50)

class ProjetoPesquisaProducaoIntelectual(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    FUNCAO = (
        ('Coordenador', 'Coordenador'),
        ('Colaborador', 'Colaborador'),
    )
    SITUACAO_ATUAL = (
        ('Concluída', 'CONCLUÍDA'),
        ('Em andamento', 'EM ANDAMENTO'),
        ('Em pausa', 'EM PAUSA'),
    )

    numero_doc = models.IntegerField()
    titulo = models.CharField(max_length=600)
    funcao = models.CharField(
        max_length=20,
        choices=FUNCAO,
        default='Coordenador'
    )
    cadastro_proped = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='Concluída'
    )

class TrabalhoCompletoPublicadoPeriodicoBoletimTecnico(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class LivroCapituloVerbetePublicado(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class TrabalhoCompletoResumoPublicadoApresentadoCongressos(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class OutraAtividadePesquisaProducaoIntelectual(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    descricao = models.CharField(max_length = 1500)

class CHSemanalAtividadesPesquisa(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE, unique=True)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class ProjetoExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    FUNCAO = (
        ('Coordenador', 'Coordenador'),
        ('Colaborador', 'Colaborador'),
    )
    SITUACAO_ATUAL = (
        ('Concluída', 'CONCLUÍDA'),
        ('Em andamento', 'EM ANDAMENTO'),
        ('Em pausa', 'EM PAUSA'),
    )
    numero_doc = models.IntegerField()
    titulo = models.CharField(max_length=600)
    funcao = models.CharField(
        max_length=20,
        choices=FUNCAO,
        default='Coordenador'
    )
    cadastro_proex = models.CharField(max_length=100)
    situacao_atual = models.CharField(
        max_length=30,
        choices=SITUACAO_ATUAL,
        default='Concluída'
    )

class EstagioExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    area_conhecimento = models.CharField(max_length=400)
    instituicao_ou_local = models.CharField(max_length=400)
    periodo = models.CharField(max_length=100)
    ch_semanal = models.FloatField()

class AtividadeEnsinoNaoFormal(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.FloatField()
    ch_semanal_primeiro_semestre = models.FloatField(null=True)
    ch_total_segundo_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField(null=True)

class OutraAtividadeExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividade = models.CharField(max_length=1500)
    ch_total_primeiro_semestre = models.FloatField()
    ch_semanal_primeiro_semestre = models.FloatField(null=True)
    ch_total_segundo_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField(null=True)

class CHSemanalAtividadesExtensao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    ch_semanal_primeiro_semestre = models.FloatField()
    ch_semanal_segundo_semestre = models.FloatField()

class DistribuicaoCHSemanal(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    semestre = models.IntegerField()
    ch_semanal_atividade_didatica = models.FloatField()
    ch_semanal_administracao = models.FloatField()
    ch_semanal_pesquisa = models.FloatField()
    ch_semanal_extensao = models.FloatField()
    ch_semanal_total = models.FloatField(null=True)

class AtividadeGestaoRepresentacao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    cargo_e_ou_funcao = models.CharField(max_length=400)
    semestre = models.IntegerField()
    ch_semanal = models.FloatField()
    ato_de_designacao = models.CharField(max_length=400)
    periodo = models.CharField(max_length=200)

class QualificacaoDocenteAcademicaProfissional(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)
    portaria_e_ou_data_de_realizacao = models.CharField(max_length=100)

class OutraInformacao(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    atividades = models.CharField(max_length=1500)

class Afastamento(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    numero_doc = models.IntegerField()
    motivacao = models.CharField(max_length = 1500)
    portaria = models.CharField(max_length= 200)

class DocumentoComprobatorio(models.Model):
    relatorio_id = models.ForeignKey(RelatorioDocente, on_delete=models.CASCADE)
    nome_pdf = models.CharField(max_length=1000)
    binary_pdf = models.BinaryField()

