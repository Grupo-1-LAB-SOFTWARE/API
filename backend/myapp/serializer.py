from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
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



class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ('id', 'username', 'nome_completo', 'perfil', 'date_joined', 'email', 'is_active', 'password')
    
    def create(self, validated_data):
        usuario = Usuario.objects.create(
            username=validated_data['username'],
            nome_completo=validated_data['nome_completo'],
            perfil=validated_data['perfil'],
            date_joined=timezone.now(),
            email=validated_data['email'],
            is_active=False,
            password = make_password(validated_data['password'])
        )
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

class DocenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Docente
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