from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from .utils import Util
from django.forms.models import model_to_dict
from myapp.models import ( BancaExaminacao, 
                          Orientando, 
                          ProjetoDePesquisa, 
                          Publicacao, 
                          Usuario,
                          AtividadeLetiva, 
                          AtividadePedagogicaComplementar, 
                          AtividadeOrientacao,
                          QualificacaoDocente, 
                          AtividadeExtensao, 
                          ProjetoExtensao, 
                          EstagioExtensao, 
                          EnsinoNaoFormal, 
                          OutrasAtividadesExtensao, 
                          AtividadeGestaoRepresentacao, 
                          RelatorioDocente )


class AtividadeLetivaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

    def create(self, validated_data):
        carga_horaria_total = int(validated_data['numero_turmas_teorico']) * int(validated_data['carga_horaria_turmas_teorico']) + int(validated_data['numero_turmas_pratico ']) * int(validated_data['carga_horaria_turmas_pratico'])

        atividade_letiva = AtividadeLetiva.objects.create(
            codigo_disciplina = validated_data['codigo_disciplina'],
            nome_disciplina = validated_data['nome_disciplina'],
            ano = validated_data['ano'],
            semestre = validated_data['semestre'],
            curso = validated_data['curso'],
            nivel = validated_data['nivel'],
            numero_turmas_teorico = validated_data['numero_turmas_teorico'],
            numero_turmas_pratico = validated_data['numero_turmas_pratico'],
            carga_horaria_turmas_teorico = validated_data['carga_horaria_turmas_teorico'],
            carga_horaria_turmas_pratico = validated_data['carga_horaria_turmas_pratico'],
            docentes_envolvidos_e_cargas_horarias = validated_data['docentes_envolvidos_e_cargas_horarias'],
            carga_horaria_total = carga_horaria_total
        )
        return atividade_letiva
    
    def update(self, atividade_letiva, validated_data):
        atividade_letiva.codigo_disciplina = validated_data.get('codigo_disciplina', atividade_letiva.codigo_disciplina)

        atividade_letiva.nome_disciplina = validated_data.get('nome_disciplina', atividade_letiva.nome_disciplina)

        atividade_letiva.ano = validated_data.get('ano', atividade_letiva.ano)

        atividade_letiva.semestre = validated_data.get('semestre', atividade_letiva.semestre)

        atividade_letiva.curso = validated_data.get('curso', atividade_letiva.curso)

        atividade_letiva.nivel = validated_data.get('nivel', atividade_letiva.nivel)

        atividade_letiva.numero_turmas_teorico = validated_data.get('numero_turmas_teorico', atividade_letiva.numero_turmas_teorico)

        atividade_letiva.numero_turmas_pratico = validated_data.get('numero_turmas_pratico', atividade_letiva.numero_turmas_pratico)

        atividade_letiva.carga_horaria_turmas_teorico = validated_data.get('carga_horaria_turmas_teorico', atividade_letiva.carga_horaria_turmas_teorico)

        atividade_letiva.carga_horaria_turmas_pratico = validated_data.get('carga_horaria_turmas_pratico', atividade_letiva.carga_horaria_turmas_pratico)

        atividade_letiva.docentes_envolvidos_e_cargas_horarias = validated_data.get('docentes_envolvidos_e_cargas_horarias', atividade_letiva.docentes_envolvidos_e_cargas_horarias)


        numero_turmas_teorico = int(atividade_letiva.numero_turmas_teorico)
        numero_turmas_pratico = int(atividade_letiva.numero_turmas_pratico)
        carga_horaria_turmas_teorico = int(atividade_letiva.carga_horaria_turmas_teorico)
        carga_horaria_turmas_pratico = int(atividade_letiva.carga_horaria_turmas_pratico)

        atividade_letiva.carga_horaria_total = (numero_turmas_teorico * carga_horaria_turmas_teorico) + (numero_turmas_pratico * carga_horaria_turmas_pratico)

        atividade_letiva.save()
        return atividade_letiva


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = '__all__'
    
    def create(self, validated_data):
        usuario = Usuario.objects.create(
            username = validated_data['username'],
            nome_completo = validated_data['nome_completo'],
            perfil = validated_data['perfil'],
            email = validated_data['email'],
            siape = validated_data['siape'],
            classe = validated_data['classe'],
            vinculo = validated_data['vinculo'],
            regime_de_trabalho = validated_data['regime_de_trabalho'],
            titulacao = validated_data['titulacao'],
            campus = validated_data['campus'],
            instituto = validated_data['instituto'],
            password = make_password(validated_data['password'])
        )
        return usuario

    def update(self, usuario, validated_data):
        usuario.username = validated_data.get('username', usuario.username)
        usuario.nome_completo = validated_data.get('nome_completo', usuario.nome_completo)
        usuario.perfil = validated_data.get('perfil', usuario.perfil)
        usuario.email = validated_data.get('email', usuario.email)
        usuario.siape = validated_data.get('siape', usuario.siape)
        usuario.classe = validated_data.get('classe', usuario.classe)
        usuario.vinculo = validated_data.get('vinculo', usuario.vinculo)
        usuario.regime_de_trabalho = validated_data.get('regime_de_trabalho', usuario.regime_de_trabalho)
        usuario.titulacao = validated_data.get('titulacao', usuario.titulacao)
        usuario.campus = validated_data.get('campus', usuario.campus)
        usuario.instituto = validated_data.get('instituto', usuario.instituto)
        usuario.password = make_password(validated_data.get('password', usuario.password))

        usuario.save()
        return usuario


class AtividadeOrientacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeOrientacao
        fields = '__all__'

class OrientandoSerializer(serializers.ModelSerializer):
    curso = CursoSerializer(many=False, required=False, read_only=True)
    atividade_orientacao = AtividadeOrientacaoSerializer(many=False, required=False, read_only=True)
    curso_nome = serializers.CharField(required=True, write_only = True)
    atividade_orientacao_pk = serializers.IntegerField(required=True, write_only=True)
    
    class Meta:
        model = Orientando
        fields = '__all__'

    def create(self, validated_data):
        curso_instance = None
        atividade_orientacao_instance = None

        try:
            curso_instance = Curso.objects.get(nome=validated_data['curso_nome'])
        except Curso.DoesNotExist:
            raise ValidationError("Não existe nenhum curso com o nome fornecido.")

        try:
            atividade_orientacao_instance = AtividadeOrientacao.objects.get(pk=validated_data['atividade_orientacao_pk'])
        except AtividadeOrientacao.DoesNotExist:
            raise ValidationError("Não existe nenhuma atividade de orientação com o id fornecido.")
        
        orientando = Orientando.objects.create(
            **validated_data,
            atividade_orientacao = atividade_orientacao_instance,
            curso=curso_instance
        )
        return orientando

    def update(self, orientando, validated_data):
        orientando.ch_semanal_1 = validated_data.get('ch_semanal_1', orientando.ch_semanal_1)
        orientando.ch_semanal_2 = validated_data.get('ch_semanal_2', orientando.ch_semanal_2)
        orientando.semestre = validated_data.get('semestre', orientando.semestre)
        orientando.nome = validated_data.get('nome', orientando.nome)
        orientando.matricula = validated_data.get('matricula', orientando.matricula)
        orientando.tipo = validated_data.get('tipo', orientando.tipo)
        orientando.nivel = validated_data.get('nivel', orientando.nivel)

        atividade_orientacao_pk = validated_data.get('atividade_orientacao_pk', None)
        if atividade_orientacao_pk is not None:
            try:
                orientando.atividade_orientacao = AtividadeOrientacao.objects.get(pk=atividade_orientacao_pk)
            except AtividadeOrientacao.DoesNotExist:
                raise ValueError("Não existe nenhum instituto com o nome fornecido.")

        orientando.atividade_orientacao.save()
        orientando.save()
        return orientando

class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

class BancaExaminacaoSerializer(serializers.ModelSerializer):
    
    class Meta: 
        models = BancaExaminacao
        fields = '__all__'

class ProjetoDePesquisaSerializer(serializers.ModelSerializer):
    
    class Meta:
        models = ProjetoDePesquisa
        fields = '__all__'

class PublicacaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = Publicacao
        fields = '__all__'

class QualificacaoDocenteSerializer(serializers.ModelSerializer):

    class Meta:
        models = QualificacaoDocente
        fields = '__all__'
class AtividadeExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = AtividadeExtensao
        fields = '__all__'
class ProjetoExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = ProjetoExtensao
        fields = '__all__'
class EstagioExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = EstagioExtensao
        fields = '__all__'
class EnsinoNaoFormalSerializer(serializers.ModelSerializer):

    class Meta:
        models = EnsinoNaoFormal
        fields = '__all__'
class OutrasAtividadesExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = OutrasAtividadesExtensao
        fields = '__all__'
class AtividadeGestaoRepresentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        models = AtividadeGestaoRepresentacao
        fields = '__all__'
class RelatorioDocenteSerializer(serializers.ModelSerializer):

    class Meta:
        models = RelatorioDocente
        fields = '__all__'