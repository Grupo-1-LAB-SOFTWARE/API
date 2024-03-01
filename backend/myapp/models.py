from email.policy import default
from pyexpat import model
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
        ('especializacao', 'Especialização'),
        ('mestre', 'Mestre'),
        ('doutor', 'Doutor'),
    )
    id = models.AutoField(primary_key=True)
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
    campus = models.ForeignKey(Campus, related_name="docente_campus", on_delete=models.DO_NOTHING)
    instituto = models.ForeignKey(Instituto, related_name="docente_instituto", on_delete=models.DO_NOTHING)
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
    docente = models.ForeignKey(Docente, related_name="usuario_docente", on_delete=models.CASCADE)


class Curso(models.Model):
    NIVEL = (
        ('bacharelado', 'Bacharelado'),
        ('licenciatura', 'Licenciatura'),
        ('tecnologo', 'Tecnólogo'),
    )
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=3)
    campus = models.ForeignKey(Campus, related_name="curso_campus", on_delete=models.DO_NOTHING)
    instituto = models.ForeignKey(Instituto, related_name="curso_instituto", on_delete=models.DO_NOTHING)
    instituto_nome = models.CharField(max_length=150)
    nivel = models.CharField(
        max_length=30,
        choices=NIVEL,
        default='bacharelado'
    )

class AtividadeLetiva(models.Model):
    codigo_disciplina = models.CharField(max_length=10)
    nome_disciplina = models.CharField(max_length=70)
    ano = models.CharField(max_length=4)
    semestre = models.IntegerField()
    curso_nome = models.CharField(max_length=150),
    curso = models.ForeignKey(Curso, related_name="atividade_letiva_curso", on_delete=models.CASCADE)
    nivel = models.IntegerField() 
    qtd_turmas = models.IntegerField()
    carga_horaria_disciplina = models.IntegerField() 
    docentes_envolvidos_e_cargas_horarias = models.JSONField()
    carga_horaria_total = models.IntegerField()

    def clean(self):
        super().clean()
        if self.carga_horaria_total > 60:
            raise ValidationError({'total': 'O valor máximo para a carga horária total é 60.'})

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
    atividade_orientacao = models.ForeignKey(AtividadeOrientacao, related_name="orientando_atividade_orientacao", on_delete=models.DO_NOTHING)


class SupervisaoAcademica(models.Model):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    semestre = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    curso = models.CharField(max_length=60)
    tipo = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    atividade_pedagogica_complementar = models.ForeignKey(AtividadePedagogicaComplementar, related_name="supervisao_atividade_pedagogica_complementar", on_delete=models.DO_NOTHING)


class PreceptoriaTutoria(models.Model):
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    tipo = models.CharField(max_length=50)
    atividade_orientacao = models.ForeignKey(AtividadeOrientacao, related_name="preceptoria_atividade_orientacao", on_delete=models.DO_NOTHING)


class BancaExaminacao(models.Model):
    nome_candidato = models.CharField(max_length=100)
    titulo_trabalho = models.CharField(max_length=100)
    ies = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    ch_semanal_1 = models.IntegerField()
    ch_semanal_2 = models.IntegerField()



class CHSemanalEnsino(models.Model):
    semestre = models.IntegerField()
    item1 = models.ForeignKey(CHSemanalAulas, related_name="ch_semanal_aulas", on_delete=models.DO_NOTHING)
    item2 = models.ForeignKey(AtividadePedagogicaComplementar, related_name="ch_atividade_pedagogica_complementar", on_delete=models.DO_NOTHING)
    item3 = models.ForeignKey(AtividadeOrientacao, related_name="ch_atividade_orientacao", on_delete=models.DO_NOTHING)
    item4 = models.ForeignKey(BancaExaminacao, related_name="ch_banca_examinacao", on_delete=models.DO_NOTHING)
    total = models.IntegerField()

    def clean(self):
        super().clean()
        if self.total > 40:
            raise ValidationError({'total': 'O valor máximo para a ch semanal total é 40.'})


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
    ano = models.CharField(max_length=4)

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


class Afastamentos(models.Model):
    cod_proex = models.CharField(max_length=50)
    motivo = models.CharField(max_length=500)
    portaria = models.CharField(max_length=50)


class RelatorioDocente(models.Model):
    data_criacao = models.DateField()
    ano_relatorio = models.IntegerField()
