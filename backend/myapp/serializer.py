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
                          RelatorioDocente,
                          CHSemanalAulas,
                          DescricaoOrientacaoCoorientacaoAcademica,
                          SupervisaoAcademica,
                          PreceptoriaTutoriaResidencia,
                          BancasExaminadoras,
                          CHSemanalAtividadeEnsino,
                          AvaliacaoDiscente,
                          ProjetoPesquisaProducao,
                          TrabalhosCompletosPeriodicosBoletins,
                          LivrosCapitulosVerbetes,
                          TrabalhosCompletosResumos,
                          OutrasAtividadesPesquisaProducao,
                          CHSemanalAtividadesPesquisa,
                          )


class AtividadeLetivaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

class SupervisaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupervisaoAcademica
        fields = '__all__'

class PreceptoriaTutoriaResidenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreceptoriaTutoriaResidencia
        fields = '__all__'

class BancasExaminadorasSerializer(serializers.ModelSerializer):

    class Meta:
        model = BancasExaminadoras
        fields = '__all__'

class CHSemanalAtividadeEnsinoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHSemanalAtividadeEnsino
        fields = '__all__'

class AvaliacaoDiscenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvaliacaoDiscente
        fields = '__all__'

class ProjetoPesquisaProducaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjetoPesquisaProducao
        fields = '__all__'

class TrabalhosCompletosPeriodicosBoletinsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhosCompletosPeriodicosBoletins
        fields = '__all__'

class LivrosCapitulosVerbetesSerializer(serializers.ModelSerializer):

    class Meta:
        model = LivrosCapitulosVerbetes
        fields = '__all__'

class TrabalhosCompletosResumosSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhosCompletosResumos
        fields = '__all__'

class OutrasAtividadesPesquisaProducaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutrasAtividadesPesquisaProducao
        fields = '__all__'

class CHSemanalAtividadesPesquisaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHSemanalAtividadesPesquisa
        fields = '__all__'




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

class DescricaoOrientacaoCoorientacaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        models = DescricaoOrientacaoCoorientacaoAcademica
        fields = '__all__'

class CHSemanalAulasSerializer(serializers.ModelSerializer):

    class Meta:
        models = CHSemanalAulas
        fields = '__all__'


class AtividadeOrientacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeOrientacao
        fields = '__all__'

class OrientandoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Orientando
        fields = '__all__'

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