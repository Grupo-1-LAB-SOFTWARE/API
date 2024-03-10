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
                          QualificacaoDocenteAcademicaProfissional
                          )


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirmar_email = serializers.EmailField(write_only=True, required=False)
    confirmar_senha = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = '__all__'
    
    def create(self, validated_data):
        confirmar_email = validated_data.pop('confirmar_email', None)
        if confirmar_email:
            if not validated_data['email'] == confirmar_email:
                raise ValidationError({'bad_request': ['confirmar_email: O campo "e-mail" deve ser igual ao campo "confirmar_email".']})
        
        confirmar_senha = validated_data.pop('confirmar_senha', None)
        if confirmar_senha:
            if not validated_data['password'] == confirmar_senha:
                raise ValidationError({'bad_request': ['confirmar_senha: O campo "password" deve ser igual ao campo "confirmar_senha".']})
            
        usuario = Usuario.objects.create(
            confirmar_email = confirmar_email,
            confirmar_senha = make_password(confirmar_senha),
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

        senha_recebida = validated_data.get('password', None)
        confirmar_senha_recebida = validated_data.get('confirmar_senha', None)
        if senha_recebida:
            if confirmar_senha_recebida:
                if not senha_recebida == confirmar_senha_recebida:
                    raise ValidationError({'bad_request': ['confirmar_senha: O campo "password" deve ser igual ao campo "confirmar_senha".']})

                usuario.confirmar_senha = make_password(confirmar_senha_recebida)
            usuario.password = make_password(senha_recebida)
    
        usuario.save()
        return usuario

class AtividadeLetivaSerializer(serializers.ModelSerializer):
    ch_total = serializers.FloatField(required=False)

    class Meta:
        model = AtividadeLetiva
        fields = '__all__'

    def create(self, validated_data):
        numero_turmas_teorico = validated_data['numero_turmas_teorico']
        numero_turmas_pratico = validated_data['numero_turmas_pratico']
        ch_turmas_teorico = validated_data['ch_turmas_teorico']
        ch_turmas_pratico = validated_data['ch_turmas_pratico']
        ch_total = (numero_turmas_teorico * ch_turmas_teorico) + (numero_turmas_pratico * ch_turmas_pratico)

        semestre = int(validated_data['semestre'])
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})

        semestre = int(validated_data['semestre'])
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})

        atividade_letiva = AtividadeLetiva.objects.create(
            **validated_data,
            ch_total = ch_total
        )
        return atividade_letiva

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            if semestre > 2 or semestre < 1:
                raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
            instance.semestre = semestre

        instance.numero_turmas_teorico = validated_data.get('numero_turmas_teorico', instance.numero_turmar_teorico)
        instance.numero_turmas_pratico = validated_data.get('numero_turmas_pratico', instance.numero_turmas_pratico)
        instance.ch_turmas_teorico = validated_data.get('ch_turmas_teorico', instance.ch_turmas_teorico)
        instance.ch_turmas_pratico = validated_data.get('ch_turmas_pratico', instance.ch_turmas_pratico)

        instance.ch_total = (instance.numero_turmas_teorico * instance.ch_turmas_teorico) + (instance.numero_turmas_pratico * instance.ch_turmas_pratico)
    
        instance.save()
        return instance

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            if semestre > 2 or semestre < 1:
                raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
            instance.semestre = semestre

        instance.numero_turmas_teorico = validated_data.get('numero_turmas_teorico', instance.numero_turmar_teorico)
        instance.numero_turmas_pratico = validated_data.get('numero_turmas_pratico', instance.numero_turmas_pratico)
        instance.ch_turmas_teorico = validated_data.get('ch_turmas_teorico', instance.ch_turmas_teorico)
        instance.ch_turmas_pratico = validated_data.get('ch_turmas_pratico', instance.ch_turmas_pratico)

        instance.ch_total = (instance.numero_turmas_teorico * instance.ch_turmas_teorico) + (instance.numero_turmas_pratico * instance.ch_turmas_pratico)
    
        instance.save()
        return instance


class CalculoCHSemanalAulasSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(required=False)
    ch_semanal_total = serializers.FloatField(required=False)

    class Meta:
        model = CalculoCHSemanalAulas
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_graduacao = validated_data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = validated_data['ch_semanal_pos_graduacao']

        ch_semanal_total = ch_semanal_graduacao + ch_semanal_pos_graduacao

        semestre = int(validated_data['semestre'])
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})

        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )
        return calculo_ch_semanal_aulas

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            if semestre > 2 or semestre < 1:
                raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
            instance.semestre = semestre

        instance.ch_semanal_graduacao = validated_data.get('ch_semanal_graduacao', instance.ch_semanal_graducao)
        instance.ch_semanal_pos_graduacao = validated_data.get('ch_semanal_pos_graduacao', instance.ch_semanal_pos_graduacao)

        instance.ch_semanal_total = instance.ch_semanal_graduacao + instance.ch_semanal_pos_graduacao
    
        instance.save()
        return instance


class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(required=False)

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_graduacao = validated_data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = validated_data['ch_semanal_pos_graduacao']

        ch_semanal_total = ch_semanal_graduacao + ch_semanal_pos_graduacao

        semestre = int(validated_data['semestre'])
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})

        atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )
        return atividade_pedagogica_complementar

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            if semestre > 2 or semestre < 1:
                raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
            instance.semestre = semestre

        instance.ch_semanal_graduacao = validated_data.get('ch_semanal_graduacao', instance.ch_semanal_graducao)
        instance.ch_semanal_pos_graduacao = validated_data.get('ch_semanal_pos_graduacao', instance.ch_semanal_pos_graduacao)

        instance.ch_semanal_total = instance.ch_semanal_graduacao + instance.ch_semanal_pos_graduacao
    
        instance.save()
        return instance


class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(required=False)

    class Meta:
        model = AtividadeOrientacaoSupervisaoPreceptoriaTutoria
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_orientacao = validated_data['ch_semanal_orientacao']
        ch_semanal_coorientacao = validated_data['ch_semanal_coorientacao']
        ch_semanal_supervisao = validated_data['ch_semanal_supervisao']
        ch_semanal_preceptoria_e_ou_tutoria = validated_data['ch_semanal_preceptoria_e_ou_tutoria']

        ch_semanal_total = ch_semanal_orientacao + ch_semanal_coorientacao + ch_semanal_supervisao + ch_semanal_preceptoria_e_ou_tutoria

        semestre = int(validated_data['semestre'])
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})

        atividades_orientacao_supervisao_preceptoria_tutoria = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )
        return atividades_orientacao_supervisao_preceptoria_tutoria

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            if semestre > 2 or semestre < 1:
                raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
            instance.semestre = semestre

        instance.ch_semanal_orientacao = validated_data.get('ch_semanal_orientacao', instance.ch_semanal_orientacao)

        instance.ch_semanal_coorientacao = validated_data.get('ch_semanal_coorientacao', instance.ch_semanal_coorientacao)

        instance.ch_semanal_supervisao = validated_data.get('ch_semanal_supervisao', instance.ch_semanal_supervisao)

        instance.ch_semanal_preceptoria_e_ou_tutoria = validated_data.get('ch_semanal_preceptoria_e_ou_tutoria', instance.ch_semanal_preceptoria_e_ou_tutoria)

        instance.ch_semanal_total = instance.ch_semanal_orientacao + instance.ch_semanal_coorientacao + instance.ch_semanal_supervisao + instance.ch_semanal_preceptoria_e_ou_tutoria
    
        instance.save()
        return instance
 

class DescricaoOrientacaoCoorientacaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DescricaoOrientacaoCoorientacaoAcademica
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
        fields = ('id', 'usuario_id', 'usuario_id', 'atividades_letivas', 'ano_relatorio', 'calculos_ch_semanal_aulas', 'atividades_pedagogicas_complementares', 'atividades_orientacao_supervisao_preceptoria_tutoria', 'descricoes_orientacao_coorientacao_academica', 'supervisoes_academicas', 'preceptorias_tutorias_residencia', 'bancas_examinadoras', 'ch_semanal_atividade_ensino',)

    def create(self, validated_data):
        #ch_semanal_atividade_ensino
        ch_semanal_atividade_ensino_data = validated_data.pop('ch_semanal_atividade_ensino', None)

        if ch_semanal_atividade_ensino_data:

            ch_semanal_atividade_ensino_serializer = CHSemanalAtividadeEnsinoSerializer(many=False, data=ch_semanal_atividade_ensino_data)
            
            if not ch_semanal_atividade_ensino_serializer.is_valid():
                raise ValidationError(f'ERRO: ch_semanal_atividade_ensino - {ch_semanal_atividade_ensino_serializer.errors}')

            ch_semanal_atividade_ensino_data = ch_semanal_atividade_ensino_serializer.data


        relatorio_docente = RelatorioDocente.objects.create(
            data_criacao = timezone.now(),

            usuario_id = validated_data['usuario_id'],

            ano_relatorio = validated_data['ano_relatorio'],

            bancas_examinadoras = bancas_examinadoras_data,

            ch_semanal_atividade_ensino = ch_semanal_atividade_ensino_data
        )
        return relatorio_docente
