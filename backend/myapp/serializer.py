from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from myapp.models import BancaExaminacao, Orientando, ProjetoDePesquisa, Publicacao, Usuario, Docente, AtividadeLetiva, AtividadePedagogicaComplementar, AtividadeOrientacao, Campus, Instituto, Curso

class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ('id', 'login', 'nome_completo', 'perfil', 'data_cadastro', 'email', 'is_email_confirmado', 'senha')
    
    def create(self, validated_data):
        user = Usuario.objects.create(
            login=validated_data['login'],
            nome_completo=validated_data['nome_completo'],
            perfil=validated_data['perfil'],
            data_cadastro=validated_data['data_cadastro'],
            email=validated_data['email'],
            is_email_confirmado=validated_data['is_email_confirmado'],
            senha = make_password(validated_data['senha'])
        )
        return user

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