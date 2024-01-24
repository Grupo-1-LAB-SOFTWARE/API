from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from myapp.models import Usuario, Docente, AtividadeLetiva, AtividadePedagogicaComplementar, AtividadeOrientacao, Campus, Instituto, Curso

class UsuarioSerializer(serializers.ModelSerializer):
    Senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ('Id', 'Login', 'NomeCompleto', 'Perfil', 'DataCadastro', 'Email', 'isEmailConfirmado')
        extra_kwargs = {'Senha': {'write_only': True}}
    
    def create(self, validated_data):
        user = Usuario.objects.create(
            Id=validated_data['Id'],
            Login=validated_data['Login'],
            NomeCompleto=validated_data['NomeCompleto'],
            Perfil=validated_data['Perfil'],
            DataCadastro=validated_data['DataCadastro'],
            Email=validated_data['Email'],
            isEmailConfirmado=validated_data['isEmailConfirmado'],
            Senha = make_password(validated_data['Senha'])
        )
        user.save()
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