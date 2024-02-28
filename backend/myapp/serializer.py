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

class CampusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campus
        fields = '__all__' 

class InstitutoSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(many=False, required=False)
    campus_nome = serializers.CharField(required=True)

    class Meta:
        model = Instituto
        fields = '__all__' 

    def create(self, validated_data):
        campus_instance = None
        try:
            campus_instance = Campus.objects.get(nome=validated_data['campus_nome'])
        except Campus.DoesNotExist:
            raise ValidationError("Não existe nenhum campus com o nome fornecido.")

        instituto = Instituto.objects.create(
            nome=validated_data['nome'],
            sigla=validated_data['sigla'],
            campus_nome = validated_data['campus_nome'],
            campus=campus_instance,
            diretor=validated_data['diretor']
        )
        return instituto
    
    def update(self, instituto, validated_data):
        instituto.nome = validated_data.get('nome', instituto.nome)
        instituto.sigla = validated_data.get('sigla', instituto.sigla)
        instituto.diretor = validated_data.get('diretor', instituto.diretor)
        
        campus_nome = validated_data.get('campus_nome', None)
        if campus_nome is not None:
            try:
                instituto.campus = Campus.objects.get(nome=campus_nome)
                instituto.campus_nome = campus_nome
            except Campus.DoesNotExist:
                raise ValidationError("Não existe nenhum campus com o nome fornecido.")

        instituto.save()
        return instituto


class DocenteSerializer(serializers.ModelSerializer):
    instituto = InstitutoSerializer(many=False, required=False)
    campus = CampusSerializer(many=False, required=False)
    instituto_nome = serializers.CharField(required=True)

    class Meta:
        model = Docente
        fields = '__all__'

    def create(self, validated_data):
        instituto_instance = None
        try:
            instituto_instance = Instituto.objects.get(nome=validated_data['instituto_nome'])
        except Instituto.DoesNotExist:
            raise ValidationError("Não existe nenhum instituto com o nome fornecido.")

        docente = Docente.objects.create(
            classe=validated_data['classe'],
            vinculo=validated_data['vinculo'],
            regime_de_trabalho=validated_data['regime_de_trabalho'],
            titulacao=validated_data['titulacao'],
            instituto_nome = validated_data['instituto_nome'],
            instituto=instituto_instance,
            campus=instituto_instance.campus
        )
        return docente

    def update(self, docente, validated_data):
        docente.classe = validated_data.get('classe', docente.classe)
        docente.vinculo = validated_data.get('vinculo', docente.vinculo)
        docente.regime_de_trabalho = validated_data.get('regime_de_trabalho', docente.regime_de_trabalho)
        docente.titulacao = validated_data.get('titulacao', docente.titulacao)
        
        
        instituto_nome = validated_data.get('instituto_nome', None)
        if instituto_nome is not None:
            try:
                docente.instituto = Instituto.objects.get(nome=instituto_nome)
                docente.instituto_nome = instituto_nome
            except Instituto.DoesNotExist:
                raise ValidationError("Não existe nenhum instituto com o nome fornecido.")

        docente.save()
        return docente

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
                usuario.docente.classe = docente_data.get('classe', usuario.docente.classe)
                usuario.docente.vinculo = docente_data.get('vinculo', usuario.docente.vinculo)
                usuario.docente.regime_de_trabalho = docente_data.get('regime_de_trabalho', usuario.docente.regime_de_trabalho)
                usuario.docente.titulacao = docente_data.get('titulacao', usuario.docente.titulacao)
                usuario.docente.campus = docente_data.get('campus', usuario.docente.campus)
                usuario.docente.instituto = docente_data.get('instituto', usuario.docente.instituto)

        usuario.docente.save()
        usuario.save()
        return usuario

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