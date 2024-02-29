from email.policy import default
from pyexpat import model
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser
from networkx import to_directed

# Create your models here.

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
    diretor = models.CharField(max_length=150)

class Instituto(models.Model):
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=3)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    campus_nome = models.CharField(max_length = 150)
    diretor = models.CharField(max_length=150)

class Docente(models.Model):
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
        ('especializacao', 'Especiallização'),
        ('mestre', 'Mestre'),
        ('doutor', 'Doutor'),
    )
    id = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=500)
    siape = models.CharField(max_length=500) #tava faltando

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
    campus = models.ForeignKey(Campus, related_name="campus", on_delete=models.DO_NOTHING)
    instituto = models.ForeignKey(Instituto, related_name="instituto", on_delete=models.DO_NOTHING)
    instituto_nome = models.CharField(max_length = 150)

class Usuario(AbstractUser):
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
    docente = models.ForeignKey(Docente, related_name="docente", on_delete=models.CASCADE)

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
    semestre = models.IntegerField()
    ch_semanal_grad = models.IntegerField()
    ch_semanal_pos_grad = models.IntegerField()
    ch_semanal_total = models.IntegerField()


class AtividadeOrientacao(models.Model):
    semestre = models.IntegerField()
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
    atividade = models.ForeignKey(AtividadePedagogicaComplementar, on_delete=models.CASCADE)


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
    semestre = models.IntegerField() 
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
    situacao = models.CharField(max_length=100)
    tipo_de_colaboracao = models.CharField(max_length=50)
    ano = models.DateField()

class Publicacao(models.Model):
    titulo = models.CharField(max_length=100)
    ano = models.IntegerField()
    veiculo_de_publicacao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)


class CHSemanalPesquisa(models.Model):
    semestre = models.IntegerField()



class AtividadeExtensao(models.Model):
    cod_proex = models.CharField(max_length=50)
    titulo = models.CharField(max_length=100)
    tipo_de_colaboracao = models.CharField(max_length=100)
    situacao = models.CharField(max_length=100)
    inicio_projeto = models.DateField()
    fim_projeto = models.DateField()
    ano = models.DateField(default='2024-02-19')

    @property
    def periodo(self):
        return f"{self.inicio_projeto} - {self.fim_projeto}"
    
class ProjetoExtensao(AtividadeExtensao):
    def __str__(self):
        return self.titulo
    
class EstagioExtensao(AtividadeExtensao):
    ch_semanal = models.IntegerField()
    def __str__(self):
        return self.titulo

class EnsinoNaoFormal(AtividadeExtensao):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    def __str__(self):
        return self.titulo
    
class OutrasAtividadesExtensao(AtividadeExtensao):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    def __str__(self):
        return self.titulo
    

class CHSemanalExtensao(models.Model):
    semestre = models.IntegerField()


class AtividadeGestaoRepresentacao(models.Model):
    cargo = models.CharField(max_length=50)
    carga_horaria_semanal = models.IntegerField()
    ato_designacao = models.CharField(max_length=100)
    inicio_projeto = models.DateField()
    fim_projeto = models.DateField()
    ano = models.DateField()

    @property
    def periodo(self):
        return f"{self.inicio_projeto} - {self.fim_projeto}"


class QualificacaoDocente(models.Model):
   cod_proex = models.CharField(max_length=50)
   atividades = models.CharField(max_length=500)
   portaria_data_realizacao = models.CharField(max_length=100)
   

class DistribuicaoCHSemanal(models.Model):
    semestre = models.IntegerField()
    atividade_didatica = models.IntegerField()
    administracao = models.IntegerField()
    pesquisa = models.IntegerField()
    extensao = models.IntegerField()
    total = models.IntegerField()


class ProgressaoPromocao(models.Model):
    OPCOES = (
        ('sim', 'Sim'),
        ('nao', "Não")
    )
    progressao_promocao = models.CharField(
        max_length=3,
        choices=OPCOES
    )
class OutrasInformacoes(models.Model):
    cod_proex = models.CharField(max_length=50)
    decricao = models.CharField(max_length=500)


class Afasamentos(models.Model):
    cod_proex = models.CharField(max_length=50)
    motivo = models.CharField(max_length=500)
    portaria = models.CharField(max_length=50)


class RelatorioDocente(models.Model):
    data_criacao = models.DateField()
    ano_relatorio = models.IntegerField()
