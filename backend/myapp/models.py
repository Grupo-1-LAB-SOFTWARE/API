from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

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
    REGIME = (
        ('exclusivo', 'Dedicação Exclusiva'),
        ('integral', 'Tempo Integral'),
        ('parcial', 'Tempo Parcial'),
    )
    id = models.AutoField(primary_key=True)
    classe = models.CharField(
        max_length=30,
        choices=CLASSE,
        default='auxiliar_1'
    )
    vinculo = models.CharField(max_length=100)
    regime_de_trabalho = models.CharField(
        max_length=50,
        choices=REGIME,
        default='exclusivo'
    )
    titulacao = models.CharField(max_length=50)
    campus = models.CharField(max_length=50)
    instituto = models.CharField(max_length=50)


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

class AtividadeLetiva(models.Model):
    codigo_disciplina = models.CharField(max_length=10)
    nome_disciplina = models.CharField(max_length=70)
    ano = models.DateField()
    semestre = models.IntegerField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    carga_horaria_disciplina = models.IntegerField()
    docentes_envolvidos = models.JSONField()
    carga_horaria_docentes_envolvidos = models.JSONField()

class AtividadePedagogicaComplementar(models.Model):
    ano = models.DateField()
    semestre = models.IntegerField()
    carga_horaria_semanal = models.IntegerField()
    docentes_envolvidos = models.JSONField()
    carga_horaria_docentes_envolvidos = models.JSONField()

class AtividadeOrientacao(models.Model):
    ano = models.IntegerField()
    semestre = models.IntegerField()
    carga_horaria = models.IntegerField()
    tipo = models.CharField(max_length=100)

class Orientando(models.Model):
    ano = models.IntegerField()
    semestre = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    curso = models.CharField(max_length=60)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    atividade = models.ForeignKey(AtividadeOrientacao, on_delete=models.CASCADE)

class BancaExaminacao(models.Model):
    nome_candidato = models.CharField(max_length=100)
    titulo_trabalho = models.CharField(max_length=100)
    ies = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    ano = models.IntegerField()
    semestre = models.IntegerField()

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
