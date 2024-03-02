from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from .utils import Util
from django.forms.models import model_to_dict
from myapp.models import ( 
                          Usuario,
                          RelatorioDocente,
                          AtividadeLetiva, 
                          CalculoCHSemanalAulas,
                          AtividadePedagogicaComplementar,
                          AtividadeOrientacaoSupervisaoPreceptoriaTutoria,
                          DescricaoOrientacaoCoorientacaoAcademica,
                          SupervisaoAcademica,
                          PreceptoriaTutoriaResidencia,
                          BancasExaminadoras,
                          CHSemanalAtividadeEnsino,
                          AvaliacaoDiscente,
                          ProjetoPesquisaProducaoIntelectual,
                          TrabalhosCompletosPeriodicosBoletinsTecnicos,
                          LivrosCapitulosVerbetesPublicados,
                          TrabalhosCompletosResumosPublicadosApresentadosCongressos,
                          OutrasAtividadesPesquisaProducaoIntelectual,
                          CHSemanalAtividadesPesquisa,
                          ProjetoExtensao, 
                          EstagioExtensao,
                          AtividadeEnsinoNaoFormal,
                          OutrasAtividasExtensao,
                          CHSemanalAtividadesExtensao,
                          DistribuicaoCHSemanal,
                          Afastamentos,
                          AtividadesGestaoRepresentacao,
                          QualificacaoDocenteAcademicaProfissional,
                          OutrasInformacoes
                          )


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


class RelatorioDocenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelatorioDocente
        fields = '__all__'


class AtividadeLetivaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

class CalculoCHSemanalAulasSerializer(serializers.ModelSerializer):

    class Meta:
        models = CalculoCHSemanalAulas
        fields = '__all__'

class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeOrientacaoSupervisaoPreceptoriaTutoria
        fields = '__all__'

class DescricaoOrientacaoCoorientacaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        models = DescricaoOrientacaoCoorientacaoAcademica
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

class ProjetoPesquisaProducaoIntelectualSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjetoPesquisaProducaoIntelectual
        fields = '__all__'

class TrabalhosCompletosPeriodicosBoletinsTecnicosSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhosCompletosPeriodicosBoletinsTecnicos
        fields = '__all__'

class LivrosCapitulosVerbetesPublicadosSerializer(serializers.ModelSerializer):

    class Meta:
        model = LivrosCapitulosVerbetesPublicados
        fields = '__all__'

class TrabalhosCompletosResumosPublicadosApresentadosCongressosSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhosCompletosResumosPublicadosApresentadosCongressos
        fields = '__all__'

class OutrasAtividadesPesquisaProducaoIntelectualSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutrasAtividadesPesquisaProducaoIntelectual
        fields = '__all__'

class CHSemanalAtividadesPesquisaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHSemanalAtividadesPesquisa
        fields = '__all__'

class ProjetoExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjetoExtensao
        fields = '__all__'


class EstagioExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = EstagioExtensao
        fields = '__all__'

class AtividadeEnsinoNaoFormalSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeEnsinoNaoFormal
        fields = '__all__'


class OutrasAtividasExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutrasAtividasExtensao
        fields = '__all__'

class CHSemanalAtividadesExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHSemanalAtividadesExtensao
        fields = '__all__'

class DistribuicaoCHSemanalSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistribuicaoCHSemanal
        fields = '__all__'

class AfastamentosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Afastamentos
        fields = '__all__'


class AtividadesGestaoRepresentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadesGestaoRepresentacao
        fields = '__all__'

class QualificacaoDocenteAcademicaProfissionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualificacaoDocenteAcademicaProfissional
        fields = '__all__'

class OutrasInformacoesSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualificacaoDocenteAcademicaProfissional
        fields = '__all__'
