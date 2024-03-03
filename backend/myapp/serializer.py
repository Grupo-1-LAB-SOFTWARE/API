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

class AtividadeLetivaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

    def calcular_ch_total(self, data):
        numero_turmas_teorico = data['numero_turmas_teorico']
        numero_turmas_pratico = data['numero_turmas_pratico']
        ch_turmas_teorico = data['ch_turmas_teorico']
        ch_turmas_pratico = data['ch_turmas_pratico']
        return (numero_turmas_teorico * ch_turmas_teorico) + (numero_turmas_pratico * ch_turmas_pratico)

    def validate(self, data):
        if data['semestre'] > 2 or data['semestre'] < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
        return data

    ch_total = serializers.SerializerMethodField(method_name='calcular_ch_total')


class CalculoCHSemanalAulasSerializer(serializers.ModelSerializer):

    class Meta:
        model = CalculoCHSemanalAulas
        fields = '__all__'

    def calcular_ch_semanal_total(self, data):
        ch_semanal_graduacao = data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = data['ch_semanal_pos_graduacao']
        return ch_semanal_graduacao + ch_semanal_pos_graduacao

    def validate(self, data):
        if data['semestre'] > 2 or data['semestre'] < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
        return data

    ch_semanal_total = serializers.SerializerMethodField(method_name='calcular_ch_semanal_total')


class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

    def calcular_ch_semanal_total(self, data):
        ch_semanal_graduacao = data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = data['ch_semanal_pos_graduacao']
        return ch_semanal_graduacao + ch_semanal_pos_graduacao

    def validate(self, data):
        if data['semestre'] > 2 or data['semestre'] < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
        return data

    ch_semanal_total = serializers.SerializerMethodField(method_name='calcular_ch_semanal_total')

class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeOrientacaoSupervisaoPreceptoriaTutoria
        fields = '__all__'

    def calcular_ch_semanal_total(self, data):
        ch_semanal_orientacao = data['ch_semanal_orientacao']
        ch_semanal_coorientacao = data['ch_semanal_coorientacao']
        ch_semanal_supervisao = data['ch_semanal_supervisao']
        ch_semanal_preceptoria_e_ou_tutoria = data['ch_semanal_preceptoria_e_ou_tutoria']
        return ch_semanal_orientacao + ch_semanal_coorientacao + ch_semanal_supervisao + ch_semanal_preceptoria_e_ou_tutoria

    def validate(self, data):
        if data['semestre'] > 2 or data['semestre'] < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
        return data

    ch_semanal_total = serializers.SerializerMethodField(method_name='calcular_ch_semanal_total')

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


class RelatorioDocenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelatorioDocente
        fields = ('ano_relatorio', 'atividades_letivas', 'calculos_ch_semanal_aulas', 'atividades_pedagogicas_complementares', 'atividades_orientacao_supervisao_preceptoria_tutoria',)

    def create(self, validated_data):
        #atividades_letivas
        atividades_letivas_data = validated_data.pop('atividades_letivas', None)

        if atividades_letivas_data:

            atividades_letivas_serializer = AtividadeLetivaSerializer(many=True, data=atividades_letivas_data)
            
            if not atividades_letivas_serializer.is_valid():
                raise ValidationError(f'ERRO: atividades_letivas - {atividades_letivas_serializer.errors}')
            
            atividades_letivas_data = atividades_letivas_serializer.data

        #calculos_ch_semanal_aulas
        calculos_ch_semanal_aulas_data = validated_data.pop('calculos_ch_semanal_aulas', None)

        if calculos_ch_semanal_aulas_data:

            calculos_ch_semanal_aulas_serializer = CalculoCHSemanalAulasSerializer(many=True, data=calculos_ch_semanal_aulas_data)
            
            if not calculos_ch_semanal_aulas_serializer.is_valid():
                raise ValidationError(f'ERRO: calculos_ch_semanal_aulas - {calculos_ch_semanal_aulas_serializer.errors}')

            calculos_ch_semanal_aulas_data = calculos_ch_semanal_aulas_serializer.data

        #atividades_pedagogicas_complementares
        atividades_pedagogicas_complementares_data = validated_data.pop('atividades_pedagogicas_complementares', None)

        if atividades_pedagogicas_complementares_data:

            atividades_pedagogicas_complementares_serializer = AtividadePedagogicaComplementarSerializer(many=True, data=atividades_pedagogicas_complementares_data)
            
            if not atividades_pedagogicas_complementares_serializer.is_valid():
                raise ValidationError(f'ERRO: atividades_pedagogicas_complementares - {atividades_pedagogicas_complementares_serializer.errors}')

            atividades_pedagogicas_complementares_data = atividades_pedagogicas_complementares_serializer.data

        #atividades_orientacao_supervisao_preceptoria_tutoria
        atividades_orientacao_supervisao_preceptoria_tutoria_data = validated_data.pop('atividades_orientacao_supervisao_preceptoria_tutoria', None)

        if atividades_orientacao_supervisao_preceptoria_tutoria_data:

            atividades_orientacao_supervisao_preceptoria_tutoria_serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(many=True, data=atividades_orientacao_supervisao_preceptoria_tutoria_data)
            
            if not atividades_orientacao_supervisao_preceptoria_tutoria_serializer.is_valid():
                raise ValidationError(f'ERRO: atividades_orientacao_supervisao_preceptoria_tutoria - {atividades_orientacao_supervisao_preceptoria_tutoria_serializer.errors}')

            atividades_orientacao_supervisao_preceptoria_tutoria_data = atividades_orientacao_supervisao_preceptoria_tutoria_serializer.data

        relatorio_docente = RelatorioDocente.objects.create(
            data_criacao = timezone.now(),
            ano_relatorio = validated_data['ano_relatorio'],
            atividades_letivas = atividades_letivas_data,
            calculos_ch_semanal_aulas = calculos_ch_semanal_aulas_data,
            atividades_pedagogicas_complementares = atividades_pedagogicas_complementares_data,
            atividades_orientacao_supervisao_preceptoria_tutoria = atividades_orientacao_supervisao_preceptoria_tutoria_data,
        )
        return relatorio_docente
