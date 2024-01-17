from django.db import models

# Create your models here.

class Usuario(models.Model):
    PERFIL = (
        ('docente', 'Docente'),
        ('admin', 'Administrador'),
    )
    Id = models.AutoField(primary_key=True)
    Login = models.CharField(max_length=13)
    NomeCompleto = models.CharField(max_length=500)
    Perfil = models.CharField(
        max_length=10,
        choices=PERFIL,
        default='docente'
    )
    DataCadastro = models.DateField()
    Email = models.EmailField()
    Senha = models.CharField(max_length=8)

class Campus(models.Model):
    CIDADE = (
        ('belem', 'Belém'),
        ('capitao_poco', 'Capitão Poço'),
    )
    Nome = models.CharField(max_length=150)
    Cidade = models.CharField(
        max_length=30,
        choices=CIDADE,
        default='belem'
    )
    Diretor = models.CharField(max_length=150),

class Instituto(models.Model):
    Nome = models.CharField(max_length=150)
    Sigla = models.CharField(max_length=3)
    Campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    Diretor = models.ForeignKey(Campus.Diretor, on_delete=models.DO_NOTHING),

class Curso(models.Model):
    NIVEL = (
        ('bacharelado', 'Bacharelado'),
        ('licenciatura', 'Licenciatura'),
        ('tecnologo', 'Tecnólogo'),
    )
    Nome = models.CharField(max_length=150),
    Sigla = models.CharField(max_length=3),
    Campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    Instituto = models.ForeignKey(Instituto, on_delete=models.DO_NOTHING)
    Nivel = models.CharField(
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
    REGIME = (
        ('exclusivo', 'Dedicação Exclusiva'),
        ('integral', 'Tempo Integral'),
        ('parcial', 'Tempo Parcial'),
    )
    Usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Id = models.AutoField(primary_key=True)
    NomeCompleto = models.CharField(max_length=500)
    Email = models.EmailField()
    Classe = models.CharField(
        max_length=30,
        choices=CLASSE,
        default='auxiliar_1'
    )
    Vinculo = models.CharField()
    RegimeDeTrabalho = models.CharField(
        max_length=50,
        choices=REGIME,
        default='exclusivo'
    )
    Titulacao = models.CharField(max_length=50)
    Campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    Instituto = models.ForeignKey(Instituto, on_delete=models.CASCADE)

    from django.db import models

class AtividadeLetiva(models.Model):
    CodigoDisciplina = models.CharField(max_length=10),
    NomeDisciplina = models.CharField(max_length=70),
    Ano = models.DateField()
    Semestre = models.IntegerField()
    Curso = models.Foreignkey(Curso, on_delete=models.CASCADE)
    CargaHorariaDisciplina = models.IntegerField()
    DocentesEnvolvidos = models.ArrayField(models.CharField(max_length=500))
    CargaHorariaDocentesEnvolvidos = models.JSONField()

class AtividadePedagogicaComplementar(models.Model):
    Ano = models.DateField()
    Semestre = models.IntegerField()
    CargaHorariaSemanal = models.IntegerField()
    DocentesEnvolvidos = models.ArrayField(models.CharField(max_length=500))
    CargaHorariaDocentesEnvolvidos = models.JSONField()

class AtividadeOrientacao(models.Model):
    ano = models.IntegerField()
    semestre = models.IntegerField()
    carga_horaria = models.IntegerField()
    tipo = models.CharField(max_lenght=100)

class Orientando(models.Model):
    ano = models.IntegerField()
    semestre = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_lenght=30)
    curso = models.CharField(max_lenght=60)
    tipo = models.CharField(max_lenght=50)
    nivel = models.CharField(max_lenght=50)
    atividade = models.ForeingKey(AtividadeOrientacao, on_delete=models.CASCADE)

class BancaExaminacao(models.Model):
    nome_candidato = models.CharField(max_lenght=100)
    titulo_trabalho = models.CharField(max_lenght=100)
    IES = models.CharField(max_lenght=100)
    tipo = models.CharField(max_lenght=50)
    ano = models.IntegerField()
    semestre = models.IntegerField()

class ProjetoDePesquisa(models.Model):
    CodigoProped = models.CharField(max_length=10)
    Titulo = models.CharField(max_length=100)
    PeriodoDoProjeto = models.JSONField()
    TipoDeColaboracao = models.CharField(max_length=50)

class Publicacao(models.Model):
    Titulo = models.CharField(max_length=100)
    Ano = models.IntegerField()
    VeiculoDePublicacao = models.CharField(max_length=100)
    Tipo = models.CharField(max_length=100)

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
    AnoDeReferencia = models.IntegerField()
    SemestreDeReferencia = models.CharField(
        max_length=1,
        choices=SEMESTRES,
        default='1')
    NivelAcademico = models.CharField(
        max_length=30,
        choices=NIVEL,
        default='pos'
    )
    AreasDePesquisa = models.ArrayField(models.CharField(max_length=200))
    CursosCapacitacao = models.ArrayField(models.CharField(max_length=300))
    ExperienciaProfissional = models.ArrayField(models.CharField(max_length=500))