from rest_framework import serializers
from django.utils import timezone
from .utils import Util
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from .utils import Util
from django.forms.models import model_to_dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
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
                          BancaExaminadora,
                          CHSemanalAtividadeEnsino,
                          AvaliacaoDiscente,
                          ProjetoPesquisaProducaoIntelectual,
                          TrabalhoCompletoPublicadoPeriodicoBoletimTecnico,
                          LivroCapituloVerbetePublicado,
                          TrabalhoCompletoResumoPublicadoApresentadoCongressos,
                          OutraAtividadePesquisaProducaoIntelectual,
                          CHSemanalAtividadesPesquisa,
                          ProjetoExtensao, 
                          EstagioExtensao,
                          AtividadeEnsinoNaoFormal,
                          OutraAtividadeExtensao,
                          CHSemanalAtividadesExtensao,
                          DistribuicaoCHSemanal,
                          Afastamento,
                          AtividadeGestaoRepresentacao,
                          QualificacaoDocenteAcademicaProfissional,
                          OutraInformacao,
                          DocumentoComprobatorio
                          )


class CustomizarTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
    
        refresh = RefreshToken.for_user(user)
        token = {
            #'refresh': str(refresh),
            'token': str(refresh.access_token)
        }

        return token

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
            password = make_password(validated_data['password']),
            is_active = False
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
    ch_total = serializers.FloatField(read_only = True)
    docentes_envolvidos_e_cargas_horarias = serializers.JSONField()

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
        Util.validar_semestre(semestre = semestre)

        docentes_envolvidos_e_cargas_horarias = validated_data.get('docentes_envolvidos_e_cargas_horarias', None)
    
        relatorio = validated_data['relatorio_id']
        usuario = relatorio.usuario_id
        nome_usuario = usuario.nome_completo.upper()

        if nome_usuario in docentes_envolvidos_e_cargas_horarias:
            ch_usuario = docentes_envolvidos_e_cargas_horarias.pop(nome_usuario, None)
            if ch_usuario:
                docentes_envolvidos_e_cargas_horarias[nome_usuario] = ch_usuario
        else:
            raise ValidationError({'docentes_envolvidos_e_cargas_horarias': ['ERRO: O usuário precisa fazer parte da atividade_letiva para cadastrá-la. Inclua uma chave igual ao "[nome do usuário em letras maiúsculas]" para se referir à carga horária do docente usuário.']})
        
        # try:
        #     atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(relatorio_id=relatorio, semestre=semestre)

        #     ch_total_atividades_letivas = 0.0
        #     calculo_ch_semanal_aulas_soma = 0.0

        #     if validated_data['nivel'] == 'GRA':
        #         atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio, semestre=semestre, nivel='GRA')
        #         for instance in atividades_letivas:
        #             ch_total_atividades_letivas = instance.docentes_envolvidos_e_cargas_horarias[nome_usuario] + ch_total_atividades_letivas

        #         ch_total_atividades_letivas = round(ch_total_atividades_letivas, 1)
        #         print(ch_total_atividades_letivas)

        #         if ch_usuario % 15 == 0:
        #             calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 15, 1)
                            
        #         else:
        #             calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 17, 1)

        #     elif validated_data['nivel'] == 'POS':
        #         atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio, semestre=semestre, nivel='POS')
        #         for instance in atividades_letivas:
        #             ch_total_atividades_letivas = instance.docentes_envolvidos_e_cargas_horarias.pop(usuario.nome_completo.upper(), None) + ch_total_atividades_letivas

        #         ch_total_atividades_letivas = round(ch_total_atividades_letivas, 1)

        #         calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 15, 1)

        #     if atividade_pedagogica_complementar:
        #         calculo_ch_semanal_aulas_soma = 2 * calculo_ch_semanal_aulas_soma

        #         if atividade_pedagogica_complementar.ch_semanal_total > calculo_ch_semanal_aulas_soma:
        #                 return Util.response_bad_request(f'ERRO: não é possível criar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a {calculo_ch_semanal_aulas_soma}.')
                    
        #         if atividade_pedagogica_complementar.ch_semanal_total > 32.0:
        #                 return Util.response_bad_request('ERRO: não é possível criar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a 32.0.')
        
        # except AtividadePedagogicaComplementar.DoesNotExist:
        #     pass

        
        atividade_letiva = AtividadeLetiva.objects.create(
            relatorio_id = validated_data['relatorio_id'],
            semestre = validated_data['semestre'],
            codigo_disciplina = validated_data['codigo_disciplina'],
            nome_disciplina = validated_data['nome_disciplina'],
            ano_e_semestre = validated_data['ano_e_semestre'],
            curso = validated_data['curso'],
            nivel = validated_data['nivel'],
            numero_turmas_teorico = validated_data['numero_turmas_teorico'],
            numero_turmas_pratico = validated_data['numero_turmas_pratico'],
            ch_turmas_teorico = validated_data['ch_turmas_teorico'],
            ch_turmas_pratico = validated_data['ch_turmas_pratico'],
            docentes_envolvidos_e_cargas_horarias = docentes_envolvidos_e_cargas_horarias,
            ch_total = ch_total
        )

        relatorio_id = atividade_letiva.relatorio_id

        Util.resetar_valores_calculos_ch_semanal_aulas(relatorio_id = relatorio_id)

        Util.recriar_calculos_ch_semanal_aulas(relatorio_id = relatorio_id)

        Util.aplicar_maximos_e_minimos_calculos_ch_semanal_aulas(relatorio_id = relatorio_id)

        return atividade_letiva

    def update(self, atividade_letiva_instance, validated_data):
        atividade_letiva_id = atividade_letiva_instance.id
        relatorio = atividade_letiva_instance.relatorio_id
        usuario = relatorio.usuario_id
        nome_usuario = usuario.nome_completo.upper()

        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
        else:
            semestre = atividade_letiva_instance.semestre

        docentes_envolvidos_e_cargas_horarias = validated_data.get('docentes_envolvidos_e_cargas_horarias', None)

        ch_usuario = None

        if docentes_envolvidos_e_cargas_horarias:
            if nome_usuario in docentes_envolvidos_e_cargas_horarias:
                ch_usuario = docentes_envolvidos_e_cargas_horarias[nome_usuario]
                atividade_letiva_instance.docentes_envolvidos_e_cargas_horarias = docentes_envolvidos_e_cargas_horarias
            else:
                raise ValidationError({'docentes_envolvidos_e_cargas_horarias': ['ERRO: O usuário precisa fazer parte da atividade_letiva para cadastrá-la. Inclua uma chave igual ao "[nome do usuário em letras maiúsculas]" para se referir à carga horária do docente usuário.']})
        else:
            docentes_envolvidos_e_cargas_horarias = atividade_letiva_instance.docentes_envolvidos_e_cargas_horarias
            ch_usuario = docentes_envolvidos_e_cargas_horarias[nome_usuario]

        # try:
        #     atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(relatorio_id=relatorio, semestre=semestre)

        #     ch_total_atividades_letivas = 0.0
        #     calculo_ch_semanal_aulas_soma = 0.0
            
        #     if validated_data.get('nivel', atividade_letiva_instance.nivel) == 'GRA':
        #         atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio, semestre=semestre, nivel='GRA')
        #         for instance in atividades_letivas:
        #             if instance.pk == atividade_letiva_id:
        #                 ch_total_atividades_letivas = docentes_envolvidos_e_cargas_horarias[nome_usuario] + ch_total_atividades_letivas
        #             else:
        #                 ch_total_atividades_letivas = instance.docentes_envolvidos_e_cargas_horarias[nome_usuario] + ch_total_atividades_letivas

        #         ch_total_atividades_letivas = round(ch_total_atividades_letivas, 1)

        #         if ch_usuario % 15 == 0:
        #             calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 15, 1)
                            
        #         else:
        #             calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 17, 1)

        #     elif validated_data.get('nivel', atividade_letiva_instance.nivel) == 'POS':
        #         atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio, semestre=semestre, nivel='POS')
        #         for instance in atividades_letivas:
        #             if instance.pk == atividade_letiva_id:
        #                 ch_total_atividades_letivas = docentes_envolvidos_e_cargas_horarias[nome_usuario] + ch_total_atividades_letivas
        #             else:
        #                 ch_total_atividades_letivas = instance.docentes_envolvidos_e_cargas_horarias[nome_usuario] + ch_total_atividades_letivas

        #         ch_total_atividades_letivas = round(ch_total_atividades_letivas, 1)

        #         calculo_ch_semanal_aulas_soma = ch_total_atividades_letivas + round(ch_usuario / 15, 1)
            
        #     if atividade_pedagogica_complementar:
        #         calculo_ch_semanal_aulas_soma = 2 * calculo_ch_semanal_aulas_soma
        #         print(calculo_ch_semanal_aulas_soma)

        #         if atividade_pedagogica_complementar.ch_semanal_total > calculo_ch_semanal_aulas_soma:
        #                 return Util.response_bad_request(f'ERRO: não é possível atualizar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a {calculo_ch_semanal_aulas_soma}.')
                    
        #         if atividade_pedagogica_complementar.ch_semanal_total > 32.0:
        #                 return Util.response_bad_request('ERRO: não é possível atualizar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a 32.0.')
        
        # except AtividadePedagogicaComplementar.DoesNotExist:
        #     pass
        
        atividade_letiva_instance.semestre = semestre

        atividade_letiva_instance.codigo_disciplina = validated_data.get('codigo_disciplina', atividade_letiva_instance.codigo_disciplina)

        atividade_letiva_instance.nome_disciplina = validated_data.get('nome_disciplina', atividade_letiva_instance.nome_disciplina)

        atividade_letiva_instance.ano_e_semestre = validated_data.get('ano_e_semestre', atividade_letiva_instance.ano_e_semestre)

        atividade_letiva_instance.curso = validated_data.get('curso', atividade_letiva_instance.curso)

        atividade_letiva_instance.nivel = validated_data.get('nivel', atividade_letiva_instance.nivel)

        atividade_letiva_instance.numero_turmas_teorico = validated_data.get('numero_turmas_teorico', atividade_letiva_instance.numero_turmas_teorico)

        atividade_letiva_instance.numero_turmas_pratico = validated_data.get('numero_turmas_pratico', atividade_letiva_instance.numero_turmas_pratico)

        atividade_letiva_instance.ch_turmas_teorico = validated_data.get('ch_turmas_teorico', atividade_letiva_instance.ch_turmas_teorico)

        atividade_letiva_instance.ch_turmas_pratico = validated_data.get('ch_turmas_pratico', atividade_letiva_instance.ch_turmas_pratico)

        atividade_letiva_instance.ch_total = (atividade_letiva_instance.numero_turmas_teorico * atividade_letiva_instance.ch_turmas_teorico) + (atividade_letiva_instance.numero_turmas_pratico * atividade_letiva_instance.ch_turmas_pratico)

        atividade_letiva_instance.save()
        
        Util.resetar_valores_calculos_ch_semanal_aulas(relatorio_id = relatorio)

        Util.recriar_calculos_ch_semanal_aulas(relatorio_id = relatorio)

        Util.aplicar_maximos_e_minimos_calculos_ch_semanal_aulas(relatorio_id=relatorio)

        return atividade_letiva_instance


class CalculoCHSemanalAulasSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(read_only = True)

    class Meta:
        model = CalculoCHSemanalAulas
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_graduacao = validated_data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = validated_data['ch_semanal_pos_graduacao']

        ch_semanal_total = ch_semanal_graduacao + ch_semanal_pos_graduacao

        semestre = int(validated_data['semestre'])
        Util.validar_semestre(semestre = semestre)

        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )
        return calculo_ch_semanal_aulas

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
            instance.semestre = semestre

        instance.ch_semanal_graduacao = validated_data.get('ch_semanal_graduacao', instance.ch_semanal_graducao)
        instance.ch_semanal_pos_graduacao = validated_data.get('ch_semanal_pos_graduacao', instance.ch_semanal_pos_graduacao)

        instance.ch_semanal_total = instance.ch_semanal_graduacao + instance.ch_semanal_pos_graduacao
    
        instance.save()
        return instance


class AtividadePedagogicaComplementarSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(read_only=True)

    class Meta:
        model = AtividadePedagogicaComplementar
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_graduacao = validated_data['ch_semanal_graduacao']
        ch_semanal_pos_graduacao = validated_data['ch_semanal_pos_graduacao']

        ch_semanal_total = ch_semanal_graduacao + ch_semanal_pos_graduacao

        semestre = int(validated_data['semestre'])
        Util.validar_semestre(semestre = semestre)

        atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )

        #Lógica POST para ch_semanal_atividade_ensino
        relatorio_id = atividade_pedagogica_complementar.relatorio_id
        ch_semanal_atividade_ensino = None
        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )
        
        if atividade_pedagogica_complementar.semestre == 1:
            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + atividade_pedagogica_complementar.ch_semanal_total
        else:
            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + atividade_pedagogica_complementar.ch_semanal_total

        ch_semanal_atividade_ensino.save()
        #Termina aqui

        return atividade_pedagogica_complementar

    def update(self, instance, validated_data):
        antigo_ch_semanal_total = instance.ch_semanal_total

        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
            instance.semestre = semestre

        instance.ch_semanal_graduacao = validated_data.get('ch_semanal_graduacao', instance.ch_semanal_graduacao)
        instance.ch_semanal_pos_graduacao = validated_data.get('ch_semanal_pos_graduacao', instance.ch_semanal_pos_graduacao)

        instance.ch_semanal_total = instance.ch_semanal_graduacao + instance.ch_semanal_pos_graduacao
    
        instance.save()

        #Lógica PUT para ch_semanal_atividade_ensino
        relatorio_id = instance.relatorio_id
        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)
            
            if instance.semestre == 1:
                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - antigo_ch_semanal_total

                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
            else:
                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - antigo_ch_semanal_total

                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )

            if instance.semestre == 1:
                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
            else:
                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total

            ch_semanal_atividade_ensino.save()
        #Termina aqui

        return instance


class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(read_only=True)

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
        Util.validar_semestre(semestre = semestre)

        atividades_orientacao_supervisao_preceptoria_tutoria = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )

        #Lógica POST para ch_semanal_atividade_ensino
        relatorio_id = atividades_orientacao_supervisao_preceptoria_tutoria.relatorio_id
        ch_semanal_atividade_ensino = None
        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )
        
        if atividades_orientacao_supervisao_preceptoria_tutoria.semestre == 1:
            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + atividades_orientacao_supervisao_preceptoria_tutoria.ch_semanal_total
        else:
            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + atividades_orientacao_supervisao_preceptoria_tutoria.ch_semanal_total

        ch_semanal_atividade_ensino.save()
        #Termina aqui

        return atividades_orientacao_supervisao_preceptoria_tutoria

    def update(self, instance, validated_data):
        antigo_ch_semanal_total = instance.ch_semanal_total

        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
            instance.semestre = semestre

        instance.ch_semanal_orientacao = validated_data.get('ch_semanal_orientacao', instance.ch_semanal_orientacao)

        instance.ch_semanal_coorientacao = validated_data.get('ch_semanal_coorientacao', instance.ch_semanal_coorientacao)

        instance.ch_semanal_supervisao = validated_data.get('ch_semanal_supervisao', instance.ch_semanal_supervisao)

        instance.ch_semanal_preceptoria_e_ou_tutoria = validated_data.get('ch_semanal_preceptoria_e_ou_tutoria', instance.ch_semanal_preceptoria_e_ou_tutoria)

        instance.ch_semanal_total = instance.ch_semanal_orientacao + instance.ch_semanal_coorientacao + instance.ch_semanal_supervisao + instance.ch_semanal_preceptoria_e_ou_tutoria
    
        instance.save()

        #Lógica PUT para ch_semanal_atividade_ensino
        relatorio_id = instance.relatorio_id
        ch_semanal_atividade_ensino = None

        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)
        
            if instance.semestre == 1:
                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - antigo_ch_semanal_total

                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
                
            else:
                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - antigo_ch_semanal_total

                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )

            if instance.semestre == 1:
                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
            else:
                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
            
            ch_semanal_atividade_ensino.save()
        #Termina aqui
                
        return instance
 

class DescricaoOrientacaoCoorientacaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DescricaoOrientacaoCoorientacaoAcademica
        fields = '__all__'

class SupervisaoAcademicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupervisaoAcademica
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_primeiro_semestre = validated_data['ch_semanal_primeiro_semestre']
        ch_semanal_segundo_semestre = validated_data['ch_semanal_segundo_semestre']
        
        if ch_semanal_primeiro_semestre > 12.0:
            raise ValidationError({'ch_semanal_primeiro_semestre': ['ERRO: A carga horária semanal de uma supervisao_academica não pode ser maior que 12 horas.']})
        
        if ch_semanal_segundo_semestre > 12.0:
            raise ValidationError({'ch_semanal_segundo_semestre': ['ERRO: A carga horária semanal de uma supervisao_academica não pode ser maior que 12 horas.']})

        supervisao_academica = SupervisaoAcademica.objects.create(
            **validated_data
        )
        return supervisao_academica

    def update(self, instance, validated_data):
        ch_semanal_primeiro_semestre = validated_data.get('ch_semanal_primeiro_semestre', None)
        if ch_semanal_primeiro_semestre:
            if ch_semanal_primeiro_semestre > 12.0:
                raise ValidationError({'ch_semanal_primeiro_semestre': ['ERRO: A carga horária semanal de uma supervisao_academica não pode ser maior que 12 horas.']})
        
        ch_semanal_segundo_semestre = validated_data.get('ch_semanal_segundo_semestre', None)
        if ch_semanal_segundo_semestre:
            if ch_semanal_segundo_semestre > 12.0:
                raise ValidationError({'ch_semanal_segundo_semestre': ['ERRO: A carga horária semanal de uma supervisao_academica não pode ser maior que 12 horas.']})
        

        instance.ch_semanal_primeiro_semestre = validated_data.get('ch_semanal_primeiro_semestre', instance.ch_semanal_primeiro_semestre)

        instance.ch_semanal_segundo_semestre = validated_data.get('ch_semanal_segundo_semestre', instance.ch_semanal_segundo_semestre)

        instance.numero_doc = validated_data.get('numero_doc', instance.numero_doc)

        instance.nome_e_ou_matricula_discente = validated_data.get('nome_e_ou_matricula_discente', instance.nome_e_ou_matricula_discente)

        instance.curso = validated_data.get('curso', instance.curso)

        instance.tipo = validated_data.get('tipo', instance.tipo)

        instance.nivel = validated_data.get('nivel', instance.nivel)
    
        instance.save()
        return instance

class PreceptoriaTutoriaResidenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreceptoriaTutoriaResidencia
        fields = '__all__'

class BancaExaminadoraSerializer(serializers.ModelSerializer):

    class Meta:
        model = BancaExaminadora
        fields = '__all__'

    def create(self, validated_data):

        banca_examinadora = BancaExaminadora.objects.create(
            **validated_data
        )

        #Lógica POST para ch_semanal_atividade_ensino
        relatorio_id = banca_examinadora.relatorio_id
        ch_semanal_atividade_ensino = None
        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )
        
        ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + banca_examinadora.ch_semanal_primeiro_semestre

        ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre + banca_examinadora.ch_semanal_segundo_semestre

        ch_semanal_atividade_ensino.save()
        #Termina aqui

        return banca_examinadora
    
    def update(self, instance, validated_data):
        antigo_ch_semanal_primeiro_semestre = instance.ch_semanal_primeiro_semestre
        antigo_ch_semanal_segundo_semestre = instance.ch_semanal_segundo_semestre

        instance.numero_doc = validated_data.get('numero_doc', instance.numero_doc)
        instance.nome_candidato = validated_data.get('nome_candidato', instance.nome_candidato)
        instance.titulo_trabalho = validated_data.get('titulo_trabalho', instance.titulo_trabalho)
        instance.ies = validated_data.get('ies', instance.ies)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.ch_semanal_primeiro_semestre = validated_data.get('ch_semanal_primeiro_semestre', instance.ch_semanal_primeiro_semestre)
        instance.ch_semanal_segundo_semestre = validated_data.get('ch_semanal_segundo_semestre', instance.ch_semanal_segundo_semestre)

        instance.save()

        #Lógica PUT para ch_semanal_atividade_ensino
        relatorio_id = instance.relatorio_id
        ch_semanal_atividade_ensino = None

        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_id)

            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - antigo_ch_semanal_primeiro_semestre

            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_primeiro_semestre
        
            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - antigo_ch_semanal_segundo_semestre

            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre + instance.ch_semanal_segundo_semestre

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )

            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_primeiro_semestre

            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre + instance.ch_semanal_segundo_semestre
            
            ch_semanal_atividade_ensino.save()
        #Termina aqui
                
        return instance

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

class TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico
        fields = '__all__'

class LivroCapituloVerbetePublicadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LivroCapituloVerbetePublicado
        fields = '__all__'

class TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrabalhoCompletoResumoPublicadoApresentadoCongressos
        fields = '__all__'

class OutraAtividadePesquisaProducaoIntelectualSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutraAtividadePesquisaProducaoIntelectual
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
    ch_semanal_primeiro_semestre = serializers.FloatField(read_only=True)
    ch_semanal_segundo_semestre = serializers.FloatField(read_only=True)

    class Meta:
        model = AtividadeEnsinoNaoFormal
        fields = '__all__'

    def create(self, validated_data):
        ch_total_primeiro_semestre = validated_data['ch_total_primeiro_semestre']
        ch_total_segundo_semestre = validated_data['ch_total_segundo_semestre']

        ch_semanal_primeiro_semestre = ch_total_primeiro_semestre / 23
        ch_semanal_segundo_semestre = ch_total_segundo_semestre / 23

        atividade_ensino_nao_formal = AtividadeEnsinoNaoFormal.objects.create(
            **validated_data,
            ch_semanal_primeiro_semestre = ch_semanal_primeiro_semestre,
            ch_semanal_segundo_semestre = ch_semanal_segundo_semestre
        )
        return atividade_ensino_nao_formal

    def update(self, instance, validated_data):
        instance.numero_doc = validated_data.get('numero_doc', instance.numero_doc)
        instance.atividade = validated_data.get('atividade', instance.atividade)

        instance.ch_total_primeiro_semestre = validated_data.get('ch_total_primeiro_semestre', instance.ch_total_primeiro_semestre)
        instance.ch_total_segundo_semestre = validated_data.get('ch_total_segundo_semestre', instance.ch_total_segundo_semestre)

        instance.ch_semanal_primeiro_semestre = instance.ch_total_primeiro_semestre / 23
        instance.ch_semanal_segundo_semestre = instance.ch_total_segundo_semestre / 23
    
        instance.save()
        return instance


class OutraAtividadeExtensaoSerializer(serializers.ModelSerializer):
    ch_semanal_primeiro_semestre = serializers.FloatField(read_only=True)
    ch_semanal_segundo_semestre = serializers.FloatField(read_only=True)

    class Meta:
        model = OutraAtividadeExtensao
        fields = '__all__'

    def create(self, validated_data):
        ch_total_primeiro_semestre = validated_data['ch_total_primeiro_semestre']
        ch_total_segundo_semestre = validated_data['ch_total_segundo_semestre']

        ch_semanal_primeiro_semestre = ch_total_primeiro_semestre / 23
        ch_semanal_segundo_semestre = ch_total_segundo_semestre / 23

        outra_atividade_extensao = OutraAtividadeExtensao.objects.create(
            **validated_data,
            ch_semanal_primeiro_semestre = ch_semanal_primeiro_semestre,
            ch_semanal_segundo_semestre = ch_semanal_segundo_semestre
        )
        return outra_atividade_extensao

    def update(self, instance, validated_data):
        instance.numero_doc = validated_data.get('numero_doc', instance.numero_doc)
        instance.atividade = validated_data.get('atividade', instance.atividade)

        instance.ch_total_primeiro_semestre = validated_data.get('ch_total_primeiro_semestre', instance.ch_total_primeiro_semestre)
        instance.ch_total_segundo_semestre = validated_data.get('ch_total_segundo_semestre', instance.ch_total_segundo_semestre)

        instance.ch_semanal_primeiro_semestre = instance.ch_total_primeiro_semestre / 23
        instance.ch_semanal_segundo_semestre = instance.ch_total_segundo_semestre / 23
    
        instance.save()
        return instance
    

class CHSemanalAtividadesExtensaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHSemanalAtividadesExtensao
        fields = '__all__'

class DistribuicaoCHSemanalSerializer(serializers.ModelSerializer):
    ch_semanal_total = serializers.FloatField(read_only=True)

    class Meta:
        model = DistribuicaoCHSemanal
        fields = '__all__'

    def create(self, validated_data):
        ch_semanal_atividade_didatica = validated_data['ch_semanal_atividade_didatica']
        ch_semanal_administracao = validated_data['ch_semanal_administracao']
        ch_semanal_pesquisa = validated_data['ch_semanal_pesquisa']
        ch_semanal_extensao = validated_data['ch_semanal_extensao']

        ch_semanal_total = ch_semanal_atividade_didatica + ch_semanal_administracao + ch_semanal_pesquisa + ch_semanal_extensao

        if ch_semanal_total > 40.0:
            raise ValidationError({'ch_semanal_total': ['A carga horária semanal total não pode ultrapassar 40 horas.']})
        
        semestre = int(validated_data['semestre'])
        Util.validar_semestre(semestre = semestre)

        distribuicao_ch_semanal = DistribuicaoCHSemanal.objects.create(
            **validated_data,
            ch_semanal_total = ch_semanal_total
        )
        return distribuicao_ch_semanal

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
            instance.semestre = semestre
        
        instance.ch_semanal_atividade_didatica = validated_data.get('ch_semanal_atividade_didatica', instance.ch_semanal_atividade_didatica)

        instance.ch_semanal_administracao = validated_data.get('ch_semanal_administracao', instance.ch_semanal_administracao)

        instance.ch_semanal_pesquisa = validated_data.get('ch_semanal_pesquisa', instance.ch_semanal_pesquisa)

        instance.ch_semanal_extensao = validated_data.get('ch_semanal_extensao', instance.ch_semanal_extensao)

        ch_semanal_total = instance.ch_semanal_atividade_didatica + instance.ch_semanal_administracao + instance.ch_semanal_pesquisa + instance.ch_semanal_extensao
        
        if ch_semanal_total > 40.0:
            raise ValidationError({'ch_semanal_total': ['A carga horária semanal total não pode ultrapassar 40 horas.']})
        
        instance.ch_semanal_total = ch_semanal_total
    
        instance.save()
        return instance

class AfastamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Afastamento
        fields = '__all__'


class AtividadeGestaoRepresentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtividadeGestaoRepresentacao
        fields = '__all__'

    def create(self, validated_data):
        semestre = int(validated_data['semestre'])
        Util.validar_semestre(semestre = semestre)

        atividade_gestao_representacao = AtividadeGestaoRepresentacao.objects.create(
            **validated_data
        )
        return atividade_gestao_representacao

    def update(self, instance, validated_data):
        semestre = validated_data.get('semestre', None)
        if semestre:
            Util.validar_semestre(semestre = semestre)
            instance.semestre = semestre
        
        instance.numero_doc = validated_data.get('numero_doc', instance.numero_doc)
        instance.cargo_e_ou_funcao = validated_data.get('cargo_e_ou_funcao', instance.cargo_e_ou_funcao)
        instance.ch_semanal = validated_data.get('ch_semanal', instance.ch_semanal)
        instance.ato_de_designacao = validated_data.get('ato_de_designacao', instance.ato_de_designacao)
        instance.periodo = validated_data.get('periodo', instance.periodo)

        instance.save()
        return instance

class QualificacaoDocenteAcademicaProfissionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualificacaoDocenteAcademicaProfissional
        fields = '__all__'

class OutraInformacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutraInformacao
        fields = '__all__'

class DocumentoComprobatorioSerializer(serializers.ModelSerializer):
    nome_pdf = serializers.CharField(read_only=True)
    binary_pdf = serializers.FileField(max_length=None, use_url=True, write_only=True)
    
    class Meta:
        model = DocumentoComprobatorio
        fields = '__all__'

    def create(self, validated_data):
        documento_pdf = validated_data.pop('binary_pdf', None)
        documento_comprobatorio = DocumentoComprobatorio.objects.create(
            binary_pdf=documento_pdf.read(),
            nome_pdf = documento_pdf.name,
            **validated_data
        )
        return documento_comprobatorio

class RelatorioDocenteSerializer(serializers.ModelSerializer):
    data_criacao = serializers.DateField(read_only=True)
    
    class Meta:
        model = RelatorioDocente
        fields = '__all__'

    def create(self, validated_data):
        relatorio_docente = RelatorioDocente.objects.create(
            data_criacao = timezone.now(),
            **validated_data
        )
        return relatorio_docente
