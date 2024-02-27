from email.policy import default
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser
from networkx import to_directed

# Create your models here.

class Usuario(AbstractUser):
    PERFIL = (
        ('docente', 'Docente'),
        ('admin', 'Administrador'),
    )
    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=13)
    nome_completo = models.CharField(max_length=500)
    perfil = models.CharField(
        max_length=10,
        choices=PERFIL,
        default='docente'
    )
    data_cadastro = models.DateField()
    email = models.EmailField()
    senha = models.CharField(max_length=8)
    is_email_confirmado = models.BooleanField(default=False)

class Campus(models.Model):
    CIDADE = (
        ('belem', 'Belém'),
        ('capitao_poco', 'Capitão Poço'),
    )
    nome = models.CharField(max_length=150)
    cidade = models.CharField(
        max_length=30,
        choices=CIDADE,
        default='belem'
    )
    diretor = models.CharField(max_length=150),

class Instituto(models.Model):
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=3)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    diretor = models.CharField(max_length=150),

class Curso(models.Model):
    NIVEL = (
        ('bacharelado', 'Bacharelado'),
        ('licenciatura', 'Licenciatura'),
        ('tecnologo', 'Tecnólogo'),
    )
    nome = models.CharField(max_length=150),
    sigla = models.CharField(max_length=3),
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    instituto = models.ForeignKey(Instituto, on_delete=models.DO_NOTHING)
    nivel = models.CharField(
        max_length=30,
        choices=NIVEL,
        default='bacharelado'
    )


class Docente(models.Model):
    CLASSE = (
        ('auxiliar_1', 'Auxiliar 1'),
        ('assistente_a_1', 'Assistente A-1'),
        ('adjunto_a_1', 'Adjunto A-1'),
        ('auxiliar_2', 'Auxiliar 2'),
        ('assistente_a_2', 'Assistente A-2'),
        ('adjunto_a_2', 'Adjunto A-2'),
        ('assistente_b_1', 'Assistente B-1'),
        ('assistente_b_2', 'Assistente B-2'),
        ('adjunto_c_1', 'Adjunto C-1'),
        ('adjunto_c_2', 'Adjunto C-2'),
        ('adjunto_c_3', 'Adjunto C-3'),
        ('adjunto_c_4', 'Adjunto C-4'),
        ('associado_d_1', 'Associado D-1'),
        ('associado_d_2', 'Associado D-2'),
        ('associado_d_3', 'Associado D-3'),
        ('associado_d_4', 'Associado D-4'),
        ('titular', 'Titular'),
    )
    # A; B; C; D; E(No formulário tem só essas opções)
    REGIME = (
        ('exclusivo', 'Dedicação Exclusiva'),
        ('integral', 'Tempo Integral'),
        ('parcial', 'Tempo Parcial'),
    )
    #DE, 40H, 20H
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=500)
    siape = models.CharField(max_length=500) #tava faltando
    email = models.EmailField() #não tem no doc
    classe = models.CharField(
        max_length=30,
        choices=CLASSE,
        default='auxiliar_1'
    )
    vinculo = models.CharField(max_length=100)
    #Estatutário(contrato formal)
    regime_de_trabalho = models.CharField(
        max_length=50,
        choices=REGIME,
        default='exclusivo'
    )
    titulacao = models.CharField(max_length=50)
    #grad, especialização, mestre, doutor
    ano = models.DateField()
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    instituto = models.ForeignKey(Instituto, on_delete=models.CASCADE)

class AtividadeLetiva(models.Model):
    codigo_disciplina = models.CharField(max_length=10)
    nome_disciplina = models.CharField(max_length=70)
    ano = models.DateField()
    semestre = models.IntegerField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    nivel =  models.IntegerField() #adicionado
    numero_turmas = models.IntegerField() #adicionado
    # T, P
    carga_horaria_disciplina = models.IntegerField() #por turma?
    # T, P 
    docentes_envolvidos = models.JSONField()
    carga_horaria_docentes_envolvidos = models.JSONField()
    carga_horaria_total = models.IntegerField(
        default = 60
    ) #adicionado
    

class CHSemanalAulas(models.Model):
    semestre = models.IntegerField()
    ch_semanal_grad = models.IntegerField()
    ch_semanal_pos_grad = models.IntegerField()
    ch_semanal_total = models.IntegerField()


class AtividadePedagogicaComplementar(models.Model):
    #ano = models.DateField()
    semestre = models.IntegerField()
    ch_semanal_grad = models.IntegerField()
    ch_semanal_pos_grad = models.IntegerField()
    ch_semanal_total = models.IntegerField()
    
    #docentes_envolvidos = models.JSONField()
    #carga_horaria_docentes_envolvidos = models.JSONField()

class AtividadeOrientacao(models.Model):
    #ano = models.IntegerField()
    semestre = models.IntegerField()
    #carga_horaria = models.IntegerField()
    #tipo = models.CharField(max_length=100)
    ch_semanal_orientacao = models.IntegerField()
    ch_semanal_coorientacao = models.IntegerField()
    ch_semanal_supervisao = models.IntegerField()
    ch_semanal_precep_tutoria = models.IntegerField()
    ch_semanal_total = models.IntegerField()

class Orientando(models.Model):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    semestre = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    curso = models.CharField(max_length=60)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    atividade = models.ForeignKey(AtividadeOrientacao, on_delete=models.CASCADE)


class SupervisaoAcademica(models.Model):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    semestre = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    curso = models.CharField(max_length=60)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    #atividade = models.ForeignKey(AtividadePedagogicaComplementar, on_delete=models.CASCADE) ?? não sei se essa relação está certa
    #Ch semanal não pode exceder 12h


class PreceptoriaTutoria(models.Model):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    tipo = models.CharField(max_length=50)
    atividade = models.ForeignKey(AtividadeOrientacao, on_delete=models.CASCADE)


class BancaExaminacao(models.Model):
    nome_candidato = models.CharField(max_length=100)
    titulo_trabalho = models.CharField(max_length=100)
    ies = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()

class CHSemanalEnsino(models.Model):
    semestre = models.IntegerField() #exitem 2 semestre para preencher
    item1 = models.ForeignKey(CHSemanalAulas, to_directed)
    item2 = models.ForeignKey(AtividadePedagogicaComplementar, to_directed)
    item3 = models.ForeignKey(AtividadeOrientacao, to_directed)
    item4 = models.ForeignKey(BancaExaminacao, to_directed)


class AvaliacaoDiscente(models.Model):
    semestre = models.IntegerField()
    numero_documento = models.IntegerField()

class ProjetoDePesquisa(models.Model):
    codigo_proped = models.CharField(max_length=10)
    titulo = models.CharField(max_length=100)
    periodo_do_projeto = models.JSONField()
    tipo_de_colaboracao = models.CharField(max_length=50)

class Publicacao(models.Model):
    titulo = models.CharField(max_length=100)
    ano = models.IntegerField()
    veiculo_de_publicacao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)

class QualificacaoDocente(models.Model):
    SEMESTRES = (
        ('1', '1'),
        ('2', '2'),
    )
    NIVELACADEMICO = (
        ('graduacao', 'Graduação'),
        ('pos', 'Pós-graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    )
    ano_de_referencia = models.IntegerField()
    semestre_de_referencia = models.CharField(
        max_length=1,
        choices=SEMESTRES,
        default='1')
    nivel_academico = models.CharField(
        max_length=30,
        choices=NIVELACADEMICO,
        default='pos'
    )
    
    #FALTA CAMPOS PARA ATIVIDADE DE PESQUISA E PRODUÇÃO INTELECTUAL

class AtividadeExtensao(models.Model):
    cod_proex = models.CharField(max_length=50)
    titulo = models.CharField(max_length=100)
    inicio_projeto = models.DateField()
    fim_projeto = models.DateField()
    tipo_de_colaboracao = models.CharField(max_length=100)

    @property
    def periodo(self):
        return f"{self.inicio_projeto} - {self.fim_projeto}"
    
class ProjetoExtensao(AtividadeExtensao):
    def __str__(self):
        return self.titulo
    
class EstagioExtensao(AtividadeExtensao):
    def __str__(self):
        return self.titulo

class EnsinoNaoFormal(AtividadeExtensao):
    def __str__(self):
        return self.titulo
    
class OutrasAtividadesExtensao(AtividadeExtensao):
    def __str__(self):
        return self.titulo

class AtividadeGestaoRepresentacao(models.Model):
    cargo = models.CharField(max_length=50)
    inicio_projeto = models.DateField()
    fim_projeto = models.DateField()
    carga_horaria_semanal = models.IntegerField()

    @property
    def periodo(self):
        return f"{self.inicio_projeto} - {self.fim_projeto}"

class RelatorioDocente(models.Model):
    data_criacao = models.DateField()
    ano_relatorio = models.IntegerField()
