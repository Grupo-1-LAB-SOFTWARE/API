from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .utils import Util
from django.forms.models import model_to_dict
from myapp.models import ( BancaExaminacao, 
                          Orientando, 
                          ProjetoDePesquisa, 
                          Publicacao, 
                          Usuario, 
                          Docente, 
                          AtividadeLetiva, 
                          AtividadePedagogicaComplementar, 
                          AtividadeOrientacao, 
                          Campus, 
                          Instituto, 
                          Curso, 
                          QualificacaoDocente, 
                          AtividadeExtensao, 
                          ProjetoExtensao, 
                          EstagioExtensao, 
                          EnsinoNaoFormal, 
                          OutrasAtividadesExtensao, 
                          AtividadeGestaoRepresentacao, 
                          RelatorioDocente )


class DocenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Docente
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    docente = DocenteSerializer(many=False)

    class Meta:
        model = Usuario
        fields = '__all__'
    
    def create(self, validated_data):
        docente_instance = None
        docente_data = validated_data.pop('docente')
        docente_serializer = DocenteSerializer(data=docente_data)
        if docente_serializer.is_valid():
            docente_instance = docente_serializer.save()
        usuario = Usuario.objects.create(
            username=validated_data['username'],
            nome_completo=validated_data['nome_completo'],
            perfil=validated_data['perfil'],
            date_joined=timezone.now(),
            email=validated_data['email'],
            is_active=False,
            password = make_password(validated_data['password']),
            docente = docente_instance
        )
        return usuario

    def update(self, usuario, validated_data):
        usuario.username = validated_data.get('username', usuario.username)
        usuario.nome_completo = validated_data.get('nome_completo', usuario.nome_completo)
        usuario.perfil = validated_data.get('perfil', usuario.perfil)
        usuario.date_joined = validated_data.get('date_joined', usuario.date_joined)
        usuario.email = validated_data.get('email', usuario.email)
        usuario.is_active = validated_data.get('is_active', usuario.is_active)
        usuario.password = make_password(validated_data.get('password', usuario.password))
        
        docente_data = validated_data.get('docente', None)
        if docente_data is not None:
            docente_serializer = DocenteSerializer(data=docente_data)
            if docente_serializer.is_valid():
                #usuario.docente.classe = validated_data.get('docente', usuario.is_active)
                Docente.objects.update_or_create(
                    pk=usuario.docente.id,
                    defaults={
                    'classe': docente_data.get('classe', usuario.docente.classe),
                    'vinculo': docente_data.get('vinculo', usuario.docente.vinculo),
                    'regime_de_trabalho': docente_data.get('regime_de_trabalho', usuario.docente.regime_de_trabalho),
                    'titulacao': docente_data.get('titulacao', usuario.docente.titulacao),
                    'campus': docente_data.get('campus', usuario.docente.campus),
                    'instituto': docente_data.get('instituto', usuario.docente.instituto)
                })
        usuario.save()
        return usuario

class CampusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campus
        fields = '__all__' 

class InstitutoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instituto
        fields = '__all__' 

class CursoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Curso
        fields = '__all__' 

class AtividadeLetivaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

class AtividadeOrientacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeOrientacao
        fields = '__all__'

class OrientandoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Orientando
        fields = '__all__'

class BancaExaminacaoSerialixer(serializers.ModelSerializer):
    
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