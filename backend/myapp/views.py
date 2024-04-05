import json
from django.utils import timezone
import tempfile
import os
import fitz 
from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.serializer import (UsuarioSerializer, RelatorioDocenteSerializer, AtividadeLetivaSerializer, CalculoCHSemanalAulasSerializer, AtividadePedagogicaComplementarSerializer, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer, DescricaoOrientacaoCoorientacaoAcademicaSerializer, SupervisaoAcademicaSerializer, PreceptoriaTutoriaResidenciaSerializer, BancaExaminadoraSerializer, CHSemanalAtividadeEnsinoSerializer, AvaliacaoDiscenteSerializer, ProjetoPesquisaProducaoIntelectualSerializer, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer, LivroCapituloVerbetePublicadoSerializer, TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer, OutraAtividadePesquisaProducaoIntelectualSerializer, CHSemanalAtividadesPesquisaSerializer, ProjetoExtensaoSerializer, EstagioExtensaoSerializer, AtividadeEnsinoNaoFormalSerializer, OutraAtividadeExtensaoSerializer, CHSemanalAtividadesExtensaoSerializer, DistribuicaoCHSemanalSerializer, AtividadeGestaoRepresentacaoSerializer, QualificacaoDocenteAcademicaProfissionalSerializer, OutraInformacaoSerializer, AfastamentoSerializer, DocumentoComprobatorioSerializer, CustomizarTokenSerializer)
from .models import (Usuario, RelatorioDocente, AtividadeLetiva, CalculoCHSemanalAulas, AtividadePedagogicaComplementar, AtividadeOrientacaoSupervisaoPreceptoriaTutoria, DescricaoOrientacaoCoorientacaoAcademica, SupervisaoAcademica, PreceptoriaTutoriaResidencia, BancaExaminadora, CHSemanalAtividadeEnsino, AvaliacaoDiscente, ProjetoPesquisaProducaoIntelectual, TrabalhoCompletoPublicadoPeriodicoBoletimTecnico, LivroCapituloVerbetePublicado, TrabalhoCompletoResumoPublicadoApresentadoCongressos, OutraAtividadePesquisaProducaoIntelectual, CHSemanalAtividadesPesquisa, ProjetoExtensao, EstagioExtensao, AtividadeEnsinoNaoFormal, OutraAtividadeExtensao, CHSemanalAtividadesExtensao, DistribuicaoCHSemanal, AtividadeGestaoRepresentacao, QualificacaoDocenteAcademicaProfissional, OutraInformacao, Afastamento, DocumentoComprobatorio)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .services import extrair_texto_do_pdf, extrair_dados_de_atividades_letivas
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

class CriarUsuarioView(APIView):
    def post(self, request):
        new_username = request.data.get('username')
        new_email = request.data.get('email')
            
        if self.is_username_disponivel(new_username) == False:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
        if self.is_email_disponivel(new_email) == False:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')

        request.data['perfil'] = 'Docente'
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_dict = model_to_dict(user)
            user_login = user_dict.get('username', None)
            user_email = user_dict.get('email', None)
            if (user_login, user_email) is not None:
                Util.send_verification_email(user_login, user_email, request)
                return Response({'id': f'{user.pk}'}, status=status.HTTP_201_CREATED)
        return Util.response_bad_request(serializer.errors)

    def is_username_disponivel(self, username):
        try:
            Usuario.objects.get(username=username)
            return False
        except Usuario.DoesNotExist:
            return True

    def is_email_disponivel(self, email):
        try:
            Usuario.objects.get(email=email)
            return False
        except Usuario.DoesNotExist:
            return True
        
class UsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instance = request.user
        
        serializer = UsuarioSerializer(instance)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request):
        instance = request.user
        
        data = request.data.copy()
        if 'id' in data:
            return Util.response_unauthorized('Não é permitido atualizar nenhum id')
        if 'is_active' in data:
            return Util.response_unauthorized('Não é permitido atualizar o campo "is_active"')
        if 'date_joined' in data:
            return Util.response_unauthorized('Não é permitido atualizar o campo "date_joined"')
        if 'perfil' in data:
            return Util.response_unauthorized('Não é permitido atualizar o campo "perfil"')
        if 'last_login' in data:
            return Util.response_unauthorized('Não é permitido atualizar o campo "last_login"')
        
        new_username = request.data.get('username')
        new_email = request.data.get('email')
        if self.is_username_disponivel(new_username) == False:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
        if self.is_email_disponivel(new_email) == False:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')
        
        serializer = UsuarioSerializer(instance, data=data, partial=True)

        if serializer.is_valid():
            usuario = serializer.save()
            if new_email:
                usuario.is_active = False
                usuario.save()
                user_dict = model_to_dict(usuario)
                user_login = user_dict.get('username', None)
                user_email = user_dict.get('email', None)
                if (user_login, user_email) is not None:
                    Util.send_verification_email(user_login, user_email, request)
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)
        
    def is_username_disponivel(self, username):
        try:
            Usuario.objects.get(username=username)
            return False
        except Usuario.DoesNotExist:
            return True

    def is_email_disponivel(self, email):
        try:
            Usuario.objects.get(email=email)
            return False
        except Usuario.DoesNotExist:
            return True
    
    def delete(self, request):
        instance = request.user
        instance.delete()
        return Util.response_ok_no_message('Usuário excluído com sucesso.')

class UsuarioAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username:
            return self.getById(request, username)
        else:
            return self.getAll(request)
            
    def put(self, request, username=None):
        if username is not None:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                user = Usuario.objects.get(username=username)
                data = request.data.copy()
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')
                if 'is_active' in data:
                    return Util.response_unauthorized('Não é permitido atualizar o campo "is_active"')
                if 'date_joined' in data:
                    return Util.response_unauthorized('Não é permitido atualizar o campo "date_joined"')
                if 'last_login' in data:
                    return Util.response_unauthorized('Não é permitido atualizar o campo "last_login"')

                new_username = request.data.get('username')
                new_email = request.data.get('email')
                if self.is_username_disponivel(new_username) == False:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
                if self.is_email_disponivel(new_email) == False:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')

                serializer = UsuarioSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    usuario = serializer.save()
                    if new_email:
                        usuario.is_active = False
                        usuario.save()
                        user_dict = model_to_dict(usuario)
                        user_login = user_dict.get('username', None)
                        user_email = user_dict.get('email', None)
                        if (user_login, user_email) is not None:
                            Util.send_verification_email(user_login, user_email, request)

                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o username fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do usuário que você deseja atualizar em usuarios/admin/{username}/')
    
    def is_username_disponivel(self, username):
        try:
            Usuario.objects.get(username=username)
            return False
        except Usuario.DoesNotExist:
            return True

    def is_email_disponivel(self, email):
        try:
            Usuario.objects.get(email=email)
            return False
        except Usuario.DoesNotExist:
            return True

    #Pra pegar todos os usuários, sem especificar username
    def getAll(self, request):
        usuario_autenticado = Usuario.objects.get(pk = request.user.id)
        if usuario_autenticado.perfil != "Administrador":
            return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
        user = Usuario.objects.all()
        serializer = UsuarioSerializer(user, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, username=None):
        if username:
            try:
                user = Usuario.objects.get(username=username)
                serializer = UsuarioSerializer(user)
                return Util.response_ok_no_message(serializer.data)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o username fornecido')
        return Util.response_bad_request('É necessário fornecer o username do usuário que você deseja ler em usuarios/admin/{username}/')
        
    def delete(self, request, username=None):
        if username:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                instance = Usuario.objects.get(username=username)
                instance.delete()
                return Util.response_ok_no_message('Usuário excluído com sucesso.')
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o username fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do usuário que você deseja excluir em usuarios/admin/{username}/')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        if email and password and username is None:
            return self.getToken(None, email, password)
        elif username and password and email is None:
            return self.getToken(username, None, password)
        else:
            return Util.response_unauthorized('É necessário fornecer email e senha ou username e senha para logar')

    def getToken(self, username, email, password):
        usuario = None
        if email and password:
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
               return Util.response_not_found('Não existe nenhum usuário cadastrado com esse e-mail.')
        elif username and password:
            try:
                usuario = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não existe nenhum usuário cadastrado com esse username.')

        if usuario:
            if usuario.is_active == False:
                return Util.response_unauthorized('O usuário fornecido não pode realizar login pois ainda não confirmou o seu e-mail.')

            if check_password(password, usuario.password):
                usuario.last_login = timezone.now()
                usuario.save(update_fields=['last_login'])
                token = CustomizarTokenSerializer.get_token(user=usuario)
                return Util.response_ok_token(token)
            else:
                return Util.response_unauthorized('Senha incorreta.')
        else:
            return Util.response_not_found('Ocorreu algum erro desconhecido')

class ActivateEmail(APIView):
    def get(self, request, username):
        try:
            Usuario.objects.filter(username=username).update(
                is_active=True
            )
        except Usuario.DoesNotExist:
            return Util.response_not_found('Usuário não encontrado')

        return Util.response_ok('Ativação do usuário bem-sucedida')

class AtividadeLetivaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_atividade_letiva=None):
        if nome_relatorio and id_atividade_letiva:
            return self.getById(request, nome_relatorio, id_atividade_letiva)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_atividade_letiva=None):
        if nome_relatorio:
            if id_atividade_letiva:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = AtividadeLetiva.objects.get(relatorio_id=relatorio_docente.pk, pk=id_atividade_letiva)
                    serializer = AtividadeLetivaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadeLetiva.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da atividade_letiva que você deseja ler em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as atividades_letivas em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AtividadeLetiva.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AtividadeLetivaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as atividades_letivas em atividade_letiva/{nome_relatorio}/')
        
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadeLetivaSerializer(data=request.data)
                if serializer.is_valid():
                    atividade_letiva = serializer.save()
                    return Util.response_created(f'id: {atividade_letiva.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma atividade_letiva em atividade_letiva/{nome_relatorio}/')

    def put(self, request, nome_relatorio=None, id_atividade_letiva=None):
        if nome_relatorio:
            if id_atividade_letiva:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    atividade_letiva = AtividadeLetiva.objects.get(pk=id_atividade_letiva, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = AtividadeLetivaSerializer(atividade_letiva, data=data, partial=True)
                    if serializer.is_valid():
                        atividade_letiva = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadeLetiva.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_letiva que você deseja atualizar em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma atividade_letiva em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')
        
    def delete(self, request, nome_relatorio=None, id_atividade_letiva=None):
        if nome_relatorio:
            if id_atividade_letiva:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    atividade_letiva = AtividadeLetiva.objects.get(pk=id_atividade_letiva, relatorio_id = relatorio_docente.pk)


                    relatorio_id = atividade_letiva.relatorio_id
                    atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio_id)
                    
                    atividades_letivas_semestre = AtividadeLetiva.objects.filter(relatorio_id=relatorio_id, semestre = atividade_letiva.semestre)

                    # if atividades_letivas_semestre.count() == 1:
                    #     atividades_pedagogicas_complementares = AtividadePedagogicaComplementar.objects.filter(relatorio_id=relatorio_id, semestre=atividade_letiva.semestre)

                    #     for instance in atividades_pedagogicas_complementares:
                    #         if instance.ch_semanal_total > 0.0:
                    #             return Util.response_bad_request('ERRO: Para deletar a atividade_letiva desejada será necessário deletar todas as atividades_pedagogicas_complementares desse mesmo semestre no radoc em questão ou atualizá-las para terem sua ch_semanal_total igual a zero.')

                    # calculo_ch_semanal_aulas_soma = 0.0
                    
                    # for instance in atividades_letivas_semestre:
                    #     if instance == atividade_letiva:
                    #         continue

                    #     ch_usuario = instance.docentes_envolvidos_e_cargas_horarias.pop(relatorio_id.usuario_id.nome_completo.upper(), None)

                    #     if instance.nivel == 'GRA':
                    #         if ch_usuario % 15 == 0:
                    #             calculo_ch_semanal_aulas_soma = calculo_ch_semanal_aulas_soma + round(ch_usuario / 15, 1)
                                
                    #         else:
                    #             calculo_ch_semanal_aulas_soma = calculo_ch_semanal_aulas_soma + round(ch_usuario / 17, 1)

                    #     elif instance.nivel == 'POS':
                    #         calculo_ch_semanal_aulas_soma = calculo_ch_semanal_aulas_soma + round(ch_usuario / 15, 1)

                    # try:
                    #     atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(relatorio_id=relatorio_id, semestre=atividade_letiva.semestre)
                        
                    #     calculo_ch_semanal_aulas_soma = 2 * calculo_ch_semanal_aulas_soma

                    #     if atividade_pedagogica_complementar.ch_semanal_total > calculo_ch_semanal_aulas_soma:
                    #         return Util.response_bad_request(f'ERRO: não é possível deletar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a {calculo_ch_semanal_aulas_soma}.')
                        
                    #     if atividade_pedagogica_complementar.ch_semanal_total > 32.0:
                    #         return Util.response_bad_request('ERRO: não é possível deletar uma atividade_letiva para esse nível e semestre sem antes atualizar a ch_semanal_total da sua atividade_pedagogica_complementar do mesmo nível e semestre para um valor menor ou igual a 32.0.')
                            
                    
                    # except AtividadePedagogicaComplementar.DoesNotExist:
                    #     pass
                            
                    if atividades_letivas_semestre.count() == 1:
                        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(relatorio_id=relatorio_id, semestre=atividade_letiva.semestre)

                        calculo_ch_semanal_aulas.delete()
        
                    atividade_letiva.delete()

                    Util.resetar_valores_calculos_ch_semanal_aulas(relatorio_id = relatorio_id)

                    Util.recriar_calculos_ch_semanal_aulas(relatorio_id = relatorio_id)

                    if atividades_letivas.count() == 0:
                        calculos_ch_semanal_aulas = CalculoCHSemanalAulas.objects.filter(relatorio_id=relatorio_id)

                        for instance in calculos_ch_semanal_aulas:
                            instance.delete()
                    else:
                        Util.aplicar_maximos_e_minimos_calculos_ch_semanal_aulas(relatorio_id=relatorio_id)

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
                
                except AtividadeLetiva.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_letiva que você deseja deletar em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma atividade_letiva em atividade_letiva/{nome_relatorio}/{id_atividade_letiva}/')
    
class AtividadePedagogicaComplementarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_atividade_pedagogica_complementar=None):
        if nome_relatorio and id_atividade_pedagogica_complementar:
            return self.getById(request, nome_relatorio, id_atividade_pedagogica_complementar)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_atividade_pedagogica_complementar=None):
        if nome_relatorio:
            if id_atividade_pedagogica_complementar:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)

                    instance = AtividadePedagogicaComplementar.objects.get(relatorio_id=relatorio_docente.pk, pk=id_atividade_pedagogica_complementar)
                    serializer = AtividadePedagogicaComplementarSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadePedagogicaComplementar.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja ler em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os calculos_ch_semanal_aulas em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AtividadePedagogicaComplementar.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AtividadePedagogicaComplementarSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as atividades_pedagogicas_complementares em atividade_pedagogica_complementar/{nome_relatorio}/')
        
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                atividade_pedagogica_complementar = None
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                try:
                    instances = AtividadePedagogicaComplementar.objects.filter(relatorio_id=relatorio_docente.pk)
                    if instances.count() > 0:
                        if instances.count() == 2:
                            return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas atividade_pedagogica_complementar para cada relatorio_docente. Uma para cada semestre.')
                        
                        for instance in instances:
                            if instance.semestre is 1 and serializer.validated_data.get('semestre') is 1:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')
                            if instance.semestre is 2 and serializer.validated_data.get('semestre') is 2:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')
                            
                except AtividadePedagogicaComplementar.DoesNotExist:
                    pass

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadePedagogicaComplementarSerializer(data=request.data)
                if serializer.is_valid():
                    try:
                        relatorio_id = serializer.validated_data.get('relatorio_id')
                        semestre = serializer.validated_data.get('semestre')

                        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(relatorio_id=relatorio_id, semestre=semestre)
                        
                        ch_semanal_total = serializer.validated_data.get('ch_semanal_graduacao') + serializer.validated_data.get('ch_semanal_pos_graduacao')

                        if ch_semanal_total > 2 * calculo_ch_semanal_aulas.ch_semanal_total:
                            return Util.response_bad_request('ERRO: não é possível criar uma atividade_pedagogica_complementar em que a soma entre ch_semanal_graduacao e ch_semanal_pos_graduacao seja maior que o dobro do ch_semanal_total do seu calculo_ch_semanal_aulas correspondente')

                    except CalculoCHSemanalAulas.DoesNotExist:
                        return Util.response_bad_request('ERRO: não é possível criar uma atividade_pedagogica_complementar para um semestre em específico sem antes criar uma atividade_letiva para o mesmo semestre.')
            
                
                    atividade_pedagogica_complementar = serializer.save()
                    return Util.response_created(f'id: {atividade_pedagogica_complementar.pk}')
                
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma atividade_pedagogica_complementar em atividade_pedagogica_complementar/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_atividade_pedagogica_complementar=None):
        if nome_relatorio:
            if id_atividade_pedagogica_complementar:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)
                    atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(pk=id_atividade_pedagogica_complementar, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = AtividadePedagogicaComplementarSerializer(atividade_pedagogica_complementar, data=data, partial=True)
                    if serializer.is_valid():
                        relatorio_id = atividade_pedagogica_complementar.relatorio_id
                        try:
                            instances = AtividadePedagogicaComplementar.objects.filter(relatorio_id=relatorio_id)

                            for instance in instances:
                                if instance.pk != id_atividade_pedagogica_complementar:
                                    if instance.semestre is 1 and serializer.validated_data.get('semestre', 2) is 1:
                                        return Util.response_bad_request('Objeto não atualizado: só pode existir uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')
                                    if instance.semestre is 2 and serializer.validated_data.get('semestre', 1) is 2:
                                        return Util.response_bad_request('Objeto não atualizado: só pode existir uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')

                        except AtividadePedagogicaComplementar.DoesNotExist:
                            return Util.response_bad_request('ERRO: Não foi possível encontrar uma atividade_pedagogica_complementar que pertença ao mesmo relatorio_docente.')
                        
                        try:
                            relatorio_id = serializer.validated_data.get('relatorio_id', atividade_pedagogica_complementar.relatorio_id)
                            semestre = serializer.validated_data.get('semestre', atividade_pedagogica_complementar.semestre)

                            calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(relatorio_id=relatorio_id, semestre=semestre)
                    
                            ch_semanal_total = serializer.validated_data.get('ch_semanal_graduacao', atividade_pedagogica_complementar.ch_semanal_graduacao) + serializer.validated_data.get('ch_semanal_pos_graduacao', atividade_pedagogica_complementar.ch_semanal_pos_graduacao)

                            if ch_semanal_total > 2 * calculo_ch_semanal_aulas.ch_semanal_total:
                                return Util.response_bad_request('ERRO: não é possível atualizar uma atividade_pedagogica_complementar em que a soma entre ch_semanal_graduacao e ch_semanal_pos_graduacao seja maior que o dobro do ch_semanal_total do seu calculo_ch_semanal_aulas correspondente')

                        except CalculoCHSemanalAulas.DoesNotExist:
                            return Util.response_bad_request('ERRO: não é possível atualizar uma atividade_pedagogica_complementar para um semestre em específico sem antes criar uma atividade_letiva para o mesmo semestre.')
                    
                        atividade_pedagogica_complementar = serializer.save()

                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadePedagogicaComplementar.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja atualizar em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma atividade_pedagogica_complementar em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')

    def delete(self, request, nome_relatorio=None, id_atividade_pedagogica_complementar=None):
        if nome_relatorio:
            if id_atividade_pedagogica_complementar:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(pk=id_atividade_pedagogica_complementar, relatorio_id = relatorio_docente.pk)
                    atividade_pedagogica_complementar.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                except AtividadePedagogicaComplementar.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um atividade_pedagogica_complementar com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja deletar em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')

class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request, nome_relatorio=None, id_atividade_orientacao_supervisao_preceptoria_tutoria=None):
        if nome_relatorio and id_atividade_orientacao_supervisao_preceptoria_tutoria:
            return self.getById(request, nome_relatorio, id_atividade_orientacao_supervisao_preceptoria_tutoria)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_atividade_orientacao_supervisao_preceptoria_tutoria=None):
        if nome_relatorio:
            if id_atividade_orientacao_supervisao_preceptoria_tutoria:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(relatorio_id=relatorio_docente.pk, pk=id_atividade_orientacao_supervisao_preceptoria_tutoria)
                    serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da atividade_orientacao_supervisao_preceptoria_tutoria que você deseja ler em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as atividades_orientacao_supervisao_preceptorias_tutorias em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as atividades_orientacao_supervisao_preceptorias_tutorias em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(data=request.data)
                if serializer.is_valid():
                    relatorio_id = relatorio_docente.pk
                    try:
                        instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.filter(relatorio_id=relatorio_id)
                        if instances.count() > 0:
                            if instances.count() == 2:
                                return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas atividades_orientacao_supervisao_preceptorias_tutorias para cada relatorio_docente. Uma para cada semestre.')
                            
                            for instance in instances:
                                if instance.semestre is 1 and serializer.validated_data.get('semestre') is 1:
                                    return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')
                                if instance.semestre is 2 and serializer.validated_data.get('semestre') is 2:
                                    return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')

                    except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                        pass

                    atividade_orientacao_supervisao_preceptoria_tutoria = serializer.save()
                    return Util.response_created(f'id: {atividade_orientacao_supervisao_preceptoria_tutoria.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma atividade_orientacao_supervisao_preceptoria_tutoria em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_atividade_orientacao_supervisao_preceptoria_tutoria=None):
        if nome_relatorio:
            if id_atividade_orientacao_supervisao_preceptoria_tutoria:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    
                    atividade_orientacao_supervisao_preceptoria_tutoria = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id_atividade_orientacao_supervisao_preceptoria_tutoria, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(atividade_orientacao_supervisao_preceptoria_tutoria, data=data, partial=True)
                    if serializer.is_valid():
                        relatorio_id = relatorio_docente.pk
                        try:
                            instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.filter(relatorio_id=relatorio_id)
                            if instances.count() > 0:
                                for instance in instances:
                                    if instance.pk != id_atividade_orientacao_supervisao_preceptoria_tutoria:
                                        if instance.semestre is 1 and serializer.validated_data.get('semestre') is 1:
                                            return Util.response_bad_request('Objeto não atualizado: só pode existir uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')
                                        if instance.semestre is 2 and serializer.validated_data.get('semestre') is 2:
                                            return Util.response_bad_request('Objeto não atualizado: só pode existir uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')

                        except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                            pass

                        atividade_orientacao_supervisao_preceptoria_tutoria = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_orientacao_supervisao_preceptoria_tutoria que você deseja atualizar em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma atividade_orientacao_supervisao_preceptoria_tutoria em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
    
    def delete(self, request, nome_relatorio=None, id_atividade_orientacao_supervisao_preceptoria_tutoria=None):
        if nome_relatorio:
            if id_atividade_orientacao_supervisao_preceptoria_tutoria:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    atividade_orientacao_supervisao_preceptoria_tutoria = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id_atividade_orientacao_supervisao_preceptoria_tutoria, relatorio_id = relatorio_docente.pk)
                    atividade_orientacao_supervisao_preceptoria_tutoria.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_orientacao_supervisao_preceptoria_tutoria que você deseja deletar em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
        
class DescricaoOrientacaoCoorientacaoAcademicaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_descricao_orientacao_coorientacao_academica=None):
        if nome_relatorio and id_descricao_orientacao_coorientacao_academica:
            return self.getById(request, nome_relatorio, id_descricao_orientacao_coorientacao_academica)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_descricao_orientacao_coorientacao_academica=None):
        if nome_relatorio:
            if id_descricao_orientacao_coorientacao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = DescricaoOrientacaoCoorientacaoAcademica.objects.get(relatorio_id=relatorio_docente.pk, pk=id_descricao_orientacao_coorientacao_academica)
                    serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da descricao_orientacao_coorientacao_academica que você deseja ler em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as descricoes_orientacoes_coorientacoes_academicas em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = DescricaoOrientacaoCoorientacaoAcademica.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as descricoes_orientacoes_coorientacoes_academicas em descricao_orientacao_coorientacao_academica/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(data=request.data)
                if serializer.is_valid():
                    descricao_orientacao_coorientacao_academica = serializer.save()
                    return Util.response_created(f'id: {descricao_orientacao_coorientacao_academica.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma descricao_orientacao_coorientacao_academica em descricao_orientacao_coorientacao_academica/{nome_relatorio}/')

    def put(self, request, nome_relatorio=None, id_descricao_orientacao_coorientacao_academica=None):
        if nome_relatorio:
            if id_descricao_orientacao_coorientacao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    descricao_orientacao_coorientacao_academica = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id_descricao_orientacao_coorientacao_academica, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(descricao_orientacao_coorientacao_academica, data=data, partial=True)
                    if serializer.is_valid():
                        descricao_orientacao_coorientacao_academica = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da descricao_orientacao_coorientacao_academica que você deseja atualizar em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma descricao_orientacao_coorientacao_academica em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')
        
    def delete(self, request, nome_relatorio=None, id_descricao_orientacao_coorientacao_academica=None):
        if nome_relatorio:
            if id_descricao_orientacao_coorientacao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    descricao_orientacao_coorientacao_academica = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id_descricao_orientacao_coorientacao_academica, relatorio_id = relatorio_docente.pk)
                    descricao_orientacao_coorientacao_academica.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da descricao_orientacao_coorientacao_academica que você deseja deletar em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')
    
class SupervisaoAcademicaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_supervisao_academica=None):
        if nome_relatorio and id_supervisao_academica:
            return self.getById(request, nome_relatorio, id_supervisao_academica)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_supervisao_academica=None):
        if nome_relatorio:
            if id_supervisao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = SupervisaoAcademica.objects.get(relatorio_id=relatorio_docente.pk, pk=id_supervisao_academica)
                    serializer = SupervisaoAcademicaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except SupervisaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da supervisao_academica que você deseja ler em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as supervisoes_academicas em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = SupervisaoAcademica.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = SupervisaoAcademicaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as supervisoes_academicas em supervisao_academica/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = SupervisaoAcademicaSerializer(data=request.data)
                if serializer.is_valid():
                    supervisao_academica = serializer.save()
                    return Util.response_created(f'id: {supervisao_academica.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma supervisao_academica em supervisao_academica/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_supervisao_academica=None):
        if nome_relatorio:
            if id_supervisao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    supervisao_academica = SupervisaoAcademica.objects.get(pk=id_supervisao_academica, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = SupervisaoAcademicaSerializer(supervisao_academica, data=data, partial=True)
                    if serializer.is_valid():
                        supervisao_academica = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except SupervisaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da supervisao_academica que você deseja atualizar em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma supervisao_academica em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')
    
    def delete(self, request, nome_relatorio=None, id_supervisao_academica=None):
        if nome_relatorio:
            if id_supervisao_academica:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    supervisao_academica = SupervisaoAcademica.objects.get(pk=id_supervisao_academica, relatorio_id = relatorio_docente.pk)
                    supervisao_academica.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except SupervisaoAcademica.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da supervisao_academica que você deseja deletar em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')
        

class PreceptoriaTutoriaResidenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_preceptoria_tutoria_residencia=None):
        if nome_relatorio and id_preceptoria_tutoria_residencia:
            return self.getById(request, nome_relatorio, id_preceptoria_tutoria_residencia)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_preceptoria_tutoria_residencia=None):
        if nome_relatorio:
            if id_preceptoria_tutoria_residencia:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = PreceptoriaTutoriaResidencia.objects.get(relatorio_id=relatorio_docente.pk, pk=id_preceptoria_tutoria_residencia)
                    serializer = PreceptoriaTutoriaResidenciaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except PreceptoriaTutoriaResidencia.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da preceptoria_tutoria_residencia que você deseja ler em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as preceptorias_tutorias_residencias em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = PreceptoriaTutoriaResidencia.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = PreceptoriaTutoriaResidenciaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as preceptorias_tutorias_residencias em preceptoria_tutoria_residencia/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = PreceptoriaTutoriaResidenciaSerializer(data=request.data)
                if serializer.is_valid():
                    preceptoria_tutoria_residencia = serializer.save()
                    return Util.response_created(f'id: {preceptoria_tutoria_residencia.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma preceptoria_tutoria_residencia em preceptoria_tutoria_residencia/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_preceptoria_tutoria_residencia=None):
        if nome_relatorio:
            if id_preceptoria_tutoria_residencia:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    preceptoria_tutoria_residencia = PreceptoriaTutoriaResidencia.objects.get(pk=id_preceptoria_tutoria_residencia, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = PreceptoriaTutoriaResidenciaSerializer(preceptoria_tutoria_residencia, data=data, partial=True)
                    if serializer.is_valid():
                        preceptoria_tutoria_residencia = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except PreceptoriaTutoriaResidencia.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da preceptoria_tutoria_residencia que você deseja atualizar em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma preceptoria_tutoria_residencia em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')
    
    def delete(self, request, nome_relatorio=None, id_preceptoria_tutoria_residencia=None):
        if nome_relatorio:
            if id_preceptoria_tutoria_residencia:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    preceptoria_tutoria_residencia = PreceptoriaTutoriaResidencia.objects.get(pk=id_preceptoria_tutoria_residencia, relatorio_id = relatorio_docente.pk)
                    preceptoria_tutoria_residencia.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except PreceptoriaTutoriaResidencia.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da preceptoria_tutoria_residencia que você deseja deletar em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')

class BancaExaminadoraView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_banca_examinadora=None):
        if nome_relatorio and id_banca_examinadora:
            return self.getById(request, nome_relatorio, id_banca_examinadora)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_banca_examinadora=None):
        if nome_relatorio:
            if id_banca_examinadora:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = BancaExaminadora.objects.get(relatorio_id=relatorio_docente.pk, pk=id_banca_examinadora)
                    serializer = BancaExaminadoraSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except BancaExaminadora.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da banca_examinadora que você deseja ler em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as bancas_examinadoras em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = BancaExaminadora.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = BancaExaminadoraSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as bancas_examinadoras em banca_examinadora/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = BancaExaminadoraSerializer(data=request.data)
                if serializer.is_valid():
                    banca_examinadora = serializer.save()
                    return Util.response_created(f'id: {banca_examinadora.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma banca_examinadora em banca_examinadora/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_banca_examinadora=None):
        if nome_relatorio:
            if id_banca_examinadora:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    banca_examinadora = BancaExaminadora.objects.get(pk=id_banca_examinadora, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = BancaExaminadoraSerializer(banca_examinadora, data=data, partial=True)
                    if serializer.is_valid():
                        banca_examinadora = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except BancaExaminadora.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da banca_examinadora que você deseja atualizar em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma banca_examinadora em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')
    
    def delete(self, request, nome_relatorio=None, id_banca_examinadora=None):
        if nome_relatorio:
            if id_banca_examinadora:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    banca_examinadora = BancaExaminadora.objects.get(pk=id_banca_examinadora, relatorio_id = relatorio_docente.pk)
                    banca_examinadora.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except BancaExaminadora.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da banca_examinadora que você deseja deletar em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')

class AvaliacaoDiscenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_avaliacao_discente=None):
        if nome_relatorio and id_avaliacao_discente:
            return self.getById(request, nome_relatorio, id_avaliacao_discente)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_avaliacao_discente=None):
        if nome_relatorio:
            if id_avaliacao_discente:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = AvaliacaoDiscente.objects.get(relatorio_id=relatorio_docente.pk, pk=id_avaliacao_discente)
                    serializer = AvaliacaoDiscenteSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AvaliacaoDiscente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da avaliacao_discente que você deseja ler em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as avaliacoes_discentes em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AvaliacaoDiscente.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AvaliacaoDiscenteSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as avaliacoes_discentes em avaliacao_discente/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AvaliacaoDiscenteSerializer(data=request.data)
                if serializer.is_valid():
                    avaliacao_discente = serializer.save()
                    return Util.response_created(f'id: {avaliacao_discente.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma avaliacao_discente em avaliacao_discente/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_avaliacao_discente=None):
        if nome_relatorio:
            if id_avaliacao_discente:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    avaliacao_discente = AvaliacaoDiscente.objects.get(pk=id_avaliacao_discente, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = AvaliacaoDiscenteSerializer(avaliacao_discente, data=data, partial=True)
                    if serializer.is_valid():
                        avaliacao_discente = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except AvaliacaoDiscente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da avaliacao_discente que você deseja atualizar em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma avaliacao_discente em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')
    
    def delete(self, request, nome_relatorio=None, id_avaliacao_discente=None):
        if nome_relatorio:
            if id_avaliacao_discente:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    avaliacao_discente = AvaliacaoDiscente.objects.get(pk=id_avaliacao_discente, relatorio_id = relatorio_docente.pk)
                    avaliacao_discente.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except AvaliacaoDiscente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da avaliacao_discente que você deseja deletar em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')

class ProjetoPesquisaProducaoIntelectualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_projeto_pesquisa_producao_intelectual=None):
        if nome_relatorio and id_projeto_pesquisa_producao_intelectual:
            return self.getById(request, nome_relatorio, id_projeto_pesquisa_producao_intelectual)
        else:
            return self.getAll(request, nome_relatorio)

    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = ProjetoPesquisaProducaoIntelectualSerializer(data=request.data)
                if serializer.is_valid():
                    projeto_pesquisa_producao_intelectual = serializer.save()
                    return Util.response_created(f'id: {projeto_pesquisa_producao_intelectual.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma projeto_pesquisa_producao_intelectual em projeto_pesquisa_producao_intelectual/{nome_relatorio}/')

    def put(self, request, nome_relatorio=None, id_projeto_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_projeto_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    projeto_pesquisa_producao_intelectual = ProjetoPesquisaProducaoIntelectual.objects.get(pk=id_projeto_pesquisa_producao_intelectual, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = ProjetoPesquisaProducaoIntelectualSerializer(projeto_pesquisa_producao_intelectual, data=data, partial=True)
                    if serializer.is_valid():
                        projeto_pesquisa_producao_intelectual = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma projeto_pesquisa_producao_intelectual com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da projeto_pesquisa_producao_intelectual que você deseja atualizar em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma projeto_pesquisa_producao_intelectual em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = ProjetoPesquisaProducaoIntelectual.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = ProjetoPesquisaProducaoIntelectualSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
        
    def getById(self, request, nome_relatorio=None, id_projeto_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_projeto_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = ProjetoPesquisaProducaoIntelectual.objects.get(relatorio_id=relatorio_docente.pk, pk=id_projeto_pesquisa_producao_intelectual)
                    serializer = ProjetoPesquisaProducaoIntelectualSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma projeto_pesquisa_producao_intelectuala com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da projeto_pesquisa_producao_intelectual que você deseja ler em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as projeto_pesquisa_producao_intelectual em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')
        
    def delete(self, request, nome_relatorio=None, id_projeto_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_projeto_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    projeto_pesquisa_producao_intelectual = ProjetoPesquisaProducaoIntelectual.objects.get(pk=id_projeto_pesquisa_producao_intelectual, relatorio_id = relatorio_docente.pk)
                    projeto_pesquisa_producao_intelectual.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma projeto_pesquisa_producao_intelectual com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da projeto_pesquisa_producao_intelectual que você deseja deletar em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')


class TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em trabalho_completo_publicado_periodico_boletim_tecnico/{id}/')

    def getAll(self, request):
        instances = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.all()
        serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(pk=id)
                serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em trabalho_completo_publicado_periodico_boletim_tecnico/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em trabalho_completo_publicado_periodico_boletim_tecnico/{id}/')

class LivroCapituloVerbetePublicadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = LivroCapituloVerbetePublicadoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = LivroCapituloVerbetePublicado.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = LivroCapituloVerbetePublicadoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um livro_capitulo_verbete_publicado com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em livro_capitulo_verbete_publicado/{id}/')

    def getAll(self, request):
        instances = LivroCapituloVerbetePublicado.objects.all()
        serializer = LivroCapituloVerbetePublicadoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = LivroCapituloVerbetePublicado.objects.get(pk=id)
                serializer = LivroCapituloVerbetePublicadoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except LivroCapituloVerbetePublicado.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um livro_capitulo_verbete_publicado com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em livro_capitulo_verbete_publicado/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = LivroCapituloVerbetePublicado.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except LivroCapituloVerbetePublicado.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um livro_capitulo_verbete_publicado com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em livro_capitulo_verbete_publicado/{id}/')

class TrabalhoCompletoResumoPublicadoApresentadoCongressosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_resumo_publicado_apresentado_congressos com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em trabalho_completo_resumo_publicado_apresentado_congressos/{id}/')

    def getAll(self, request):
        instances = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.all()
        serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, id=None):
        if id:
            try:
                instance = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(pk=id)
                serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_resumo_publicado_apresentado_congressos com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em trabalho_completo_resumo_publicado_apresentado_congressos/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um trabalho_completo_resumo_publicado_apresentado_congressos com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em trabalho_completo_resumo_publicado_apresentado_congressos/{id}/')
    

class OutraAtividadePesquisaProducaoIntelectualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = OutraAtividadePesquisaProducaoIntelectual.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em outra_atividade_pesquisa_producao_intelectual/{id}/')

    def getAll(self, request):
        instances = OutraAtividadePesquisaProducaoIntelectual.objects.all()
        serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = OutraAtividadePesquisaProducaoIntelectual.objects.get(pk=id)
                serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em outra_atividade_pesquisa_producao_intelectual/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = OutraAtividadePesquisaProducaoIntelectual.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em outra_atividade_pesquisa_producao_intelectual/{id}/')


class CHSemanalAtividadesPesquisaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        instance = None
        serializer = CHSemanalAtividadesPesquisaSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = CHSemanalAtividadesPesquisa.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 1:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionada uma ch_semanal_atividades_pesquisa para cada relatorio_docente.')
                
                instance = serializer.save()

            except CHSemanalAtividadesPesquisa.DoesNotExist:
                instance = serializer.save()
            
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = CHSemanalAtividadesPesquisa.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = CHSemanalAtividadesPesquisaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except CHSemanalAtividadesPesquisa.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em ch_semanal_atividades_pesquisa/{id}/')

    def getAll(self, request):
        instances = CHSemanalAtividadesPesquisa.objects.all()
        serializer = CHSemanalAtividadesPesquisaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadesPesquisa.objects.get(pk=id)
                serializer = CHSemanalAtividadesPesquisaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except CHSemanalAtividadesPesquisa.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em ch_semanal_atividades_pesquisa/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadesPesquisa.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except CHSemanalAtividadesPesquisa.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em ch_semanal_atividades_pesquisa/{id}/')
        
        
class ProjetoExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = ProjetoExtensaoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = ProjetoExtensao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = ProjetoExtensaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except ProjetoExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um projeto_extensao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em projeto_extensao/{id}/')

    def getAll(self, request):
        instances = ProjetoExtensao.objects.all()
        serializer = ProjetoExtensaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = ProjetoExtensao.objects.get(pk=id)
                serializer = ProjetoExtensaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except ProjetoExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um projeto_extensao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em projeto_extensao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = ProjetoExtensao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except ProjetoExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um projeto_extensao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em projeto_extensao/{id}/')
    
        
class EstagioExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = EstagioExtensaoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = EstagioExtensao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = EstagioExtensaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except EstagioExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um estagio_extensao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em estagio_extensao/{id}/')

    def getAll(self, request):
        instances = EstagioExtensao.objects.all()
        serializer = EstagioExtensaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = EstagioExtensao.objects.get(pk=id)
                serializer = EstagioExtensaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except EstagioExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um estagio_extensao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em estagio_extensao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = EstagioExtensao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except EstagioExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um estagio_extensao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em estagio_extensao/{id}/')
        
class AtividadeEnsinoNaoFormalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = AtividadeEnsinoNaoFormalSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = AtividadeEnsinoNaoFormal.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AtividadeEnsinoNaoFormalSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeEnsinoNaoFormal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em atividade_ensino_nao_formal/{id}/')

    def getAll(self, request):
        instances = AtividadeEnsinoNaoFormal.objects.all()
        serializer = AtividadeEnsinoNaoFormalSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = AtividadeEnsinoNaoFormal.objects.get(pk=id)
                serializer = AtividadeEnsinoNaoFormalSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AtividadeEnsinoNaoFormal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em atividade_ensino_nao_formal/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AtividadeEnsinoNaoFormal.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AtividadeEnsinoNaoFormal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em atividade_ensino_nao_formal/{id}/')
    

class OutraAtividadeExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = OutraAtividadeExtensaoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = OutraAtividadeExtensao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = OutraAtividadeExtensaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except OutraAtividadeExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em outra_atividade_extensao/{id}/')

    def getAll(self, request):
        instances = OutraAtividadeExtensao.objects.all()
        serializer = OutraAtividadeExtensaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = OutraAtividadeExtensao.objects.get(pk=id)
                serializer = OutraAtividadeExtensaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except OutraAtividadeExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em outra_atividade_extensao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = OutraAtividadeExtensao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except OutraAtividadeExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em outra_atividade_extensao/{id}/')
    
class CHSemanalAtividadesExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        instance = None
        serializer = CHSemanalAtividadesExtensaoSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = CHSemanalAtividadesExtensao.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 1:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionada uma ch_semanal_atividades_extensao para cada relatorio_docente.')
                
                instance = serializer.save()

            except CHSemanalAtividadesExtensao.DoesNotExist:
                instance = serializer.save()
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = CHSemanalAtividadesExtensao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = CHSemanalAtividadesExtensaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except CHSemanalAtividadesExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em ch_semanal_atividades_extensao/{id}/')

    def getAll(self, request):
        instances = CHSemanalAtividadesExtensao.objects.all()
        serializer = CHSemanalAtividadesExtensaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadesExtensao.objects.get(pk=id)
                serializer = CHSemanalAtividadesExtensaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except CHSemanalAtividadesExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em ch_semanal_atividades_extensao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadesExtensao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except CHSemanalAtividadesExtensao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em ch_semanal_atividades_extensao/{id}/')
    
class DistribuicaoCHSemanalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        instance = None
        serializer = DistribuicaoCHSemanalSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = DistribuicaoCHSemanal.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 2:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas distribuicao_ch_semanal para cada relatorio_docente. Uma para cada semestre.')
                    
                    for instance in instances:
                        if instance.semestre is 1 and serializer.validated_data.get('semestre') is 1:
                            return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma distribuicao_ch_semanal por semestre para cada relatorio_docente.')
                        if instance.semestre is 2 and serializer.validated_data.get('semestre') is 2:
                            return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma distribuicao_ch_semanal por semestre para cada relatorio_docente.')
                
                instance = serializer.save()

            except DistribuicaoCHSemanal.DoesNotExist:
                instance = serializer.save()

            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = DistribuicaoCHSemanal.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = DistribuicaoCHSemanalSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except DistribuicaoCHSemanal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma distribuicao_ch_semanal com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em distribuicao_ch_semanal/{id}/')

    def getAll(self, request):
        instances = DistribuicaoCHSemanal.objects.all()
        serializer = DistribuicaoCHSemanalSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = DistribuicaoCHSemanal.objects.get(pk=id)
                serializer = DistribuicaoCHSemanalSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except DistribuicaoCHSemanal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma distribuicao_ch_semanal com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em distribuicao_ch_semanal/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = DistribuicaoCHSemanal.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except DistribuicaoCHSemanal.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma distribuicao_ch_semanal com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em distribuicao_ch_semanal/{id}/')
    
class AtividadeGestaoRepresentacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = AtividadeGestaoRepresentacaoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = AtividadeGestaoRepresentacao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AtividadeGestaoRepresentacaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeGestaoRepresentacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em atividade_gestao_representacao/{id}/')

    def getAll(self, request):
        instances = AtividadeGestaoRepresentacao.objects.all()
        serializer = AtividadeGestaoRepresentacaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = AtividadeGestaoRepresentacao.objects.get(pk=id)
                serializer = AtividadeGestaoRepresentacaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AtividadeGestaoRepresentacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em atividade_gestao_representacao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AtividadeGestaoRepresentacao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AtividadeGestaoRepresentacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em atividade_gestao_representacao/{id}/')
    
class QualificacaoDocenteAcademicaProfissionalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = QualificacaoDocenteAcademicaProfissionalSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = QualificacaoDocenteAcademicaProfissional.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = QualificacaoDocenteAcademicaProfissionalSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em qualificacao_docente_academica_profissional/{id}/')

    def getAll(self, request):
        instances = QualificacaoDocenteAcademicaProfissional.objects.all()
        serializer = QualificacaoDocenteAcademicaProfissionalSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = QualificacaoDocenteAcademicaProfissional.objects.get(pk=id)
                serializer = QualificacaoDocenteAcademicaProfissionalSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em qualificacao_docente_academica_profissional/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = QualificacaoDocenteAcademicaProfissional.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em qualificacao_docente_academica_profissional/{id}/')
    

class OutraInformacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = OutraInformacaoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = OutraInformacao.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = OutraInformacaoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except OutraInformacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em outra_informacao/{id}/')

    def getAll(self, request):
        instances = OutraInformacao.objects.all()
        serializer = OutraInformacaoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = OutraInformacao.objects.get(pk=id)
                serializer = OutraInformacaoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except OutraInformacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em outra_informacao/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = OutraInformacao.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except OutraInformacao.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em outra_informacao/{id}/')
    
class AfastamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = AfastamentoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = Afastamento.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AfastamentoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except Afastamento.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um afastamento com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em afastamento/{id}/')

    def getAll(self, request):
        instances = Afastamento.objects.all()
        serializer = AfastamentoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id=None):
        if id:
            try:
                instance = Afastamento.objects.get(pk=id)
                serializer = AfastamentoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except Afastamento.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um afastamento com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em afastamento/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = Afastamento.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except Afastamento.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um afastamento com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em afastamento/{id}/')
    
class DocumentoComprobatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = DocumentoComprobatorioSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)
    
    def put(self, request, id=None):
        if id is not None:
            try:
                instance = DocumentoComprobatorio.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')
                serializer = DocumentoComprobatorioSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)
            except DocumentoComprobatorio.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em documento_comprobatorio/{id}/')
    def getAll(self, request):
        instances = DocumentoComprobatorio.objects.all()
        serializer = DocumentoComprobatorioSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, id=None):
        if id:
            try:
                instance = DocumentoComprobatorio.objects.get(pk=id)
                binary_data = instance.binary_pdf
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(binary_data)
                    temp_file.seek(0)

                    # Retorna o arquivo PDF diretamente como resposta
                    response = HttpResponse(temp_file, content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{temp_file.name}"'
                    return response

            except DocumentoComprobatorio.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em documento_comprobatorio/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = DocumentoComprobatorio.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except DocumentoComprobatorio.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em documento_comprobatorio/{id}/')

class RelatorioDocenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario_id = request.user.id
        request.data['usuario_id'] = usuario_id
        try:
            relatorio_docente_existente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=request.data['nome'])
            if relatorio_docente_existente:
                return Util.response_bad_request('Já existe um relatorio_docente pertencente ao seu usuário com esse nome.')
        except RelatorioDocente.DoesNotExist:
            pass

        serializer = RelatorioDocenteSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_docente = serializer.save()
            return Util.response_created({'id': f'{relatorio_docente.pk}'})
        return Util.response_bad_request(serializer.errors)
    
    def get(self, request, nome=None):
        if nome:
            return self.getOneByUser(request, nome)
        else:
            return self.getAllByUser(request)
        
    def getAllByUser(self, request):
        instances = RelatorioDocente.objects.filter(usuario_id = request.user.id)
        serializer = RelatorioDocenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getOneByUser(self, request, nome=None):
        if nome:
            try:
                instance = RelatorioDocente.objects.get(usuario_id = request.user.id, nome=nome)
                if instance:
                    serializer = RelatorioDocenteSerializer(instance, many=True)
                    return Util.response_ok_no_message(serializer.data)
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('O usuário não possui nenhum relatorio_docente com esse nome.')
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja ler.')
    
    def delete(self, request, nome=None):
        if nome:
            try:
                instance = RelatorioDocente.objects.get(usuario_id = request.user.id, nome=nome)
                if instance:
                    instance.delete()
                    return Util.response_ok_no_message('RADOC excluído com sucesso.')
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma relatorio_docente pertencente ao usuário que tenha o nome fornecido.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja deletar.')
    
class RelatorioDocenteAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None, user_id=None):
        if id:
            return self.getById(request, id)
        elif user_id:
            return self.getByUser(request, user_id)
        else:
            return self.getAll(request)
        
    def getAll(self, request):
        usuario_autenticado = Usuario.objects.get(pk = request.user.id)
        if usuario_autenticado.perfil != "Administrador":
            return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
        
        instances = RelatorioDocente.objects.all()
        serializer = RelatorioDocenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getByUser(self, request, user_id=None):
        if user_id:
            try:
                Usuario.objects.get(pk=user_id)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não existe nenhum usuário que possua esse id.')
                
            instances = RelatorioDocente.objects.filter(usuario_id = user_id)
            serializer = RelatorioDocenteSerializer(instances, many=True)
            return Util.response_ok_no_message(serializer.data)
        
        return Util.response_bad_request('É necessário fornecer o id do usuário o qual você deseja obter os radocs criados em relatorio_docente/admin/usuario/{id}/')
    
    def getById(self, request, id=None):
        if id:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                instance = RelatorioDocente.objects.get(pk=id)
                serializer = RelatorioDocenteSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em relatorio_docente/admin/{id}/')
        
    def delete(self, request, id=None):
        if id:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                instance = RelatorioDocente.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('RADOC excluído com sucesso.')
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma relatorio_docente com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em relatorio_docente/admin/{id}/')
    
class DownloadRelatorioDocenteView(APIView):
    permission_classes = [IsAuthenticated]

    def is_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)  # Tente abrir o arquivo como um PDF
            doc.close()  # Feche o arquivo
            return True  # Se abrir sem erros, é um PDF válido
        except Exception as e:
            return False
    
    def get(self, request, relatorio_id=None):
        if relatorio_id:
            try:
                instance = RelatorioDocente.objects.get(pk=relatorio_id)
                output_pdf = PdfWriter()

                with tempfile.NamedTemporaryFile(delete=False) as temp_file_radoc:
                # Aqui será inserida a lógica de preenchimento de RADOC
                    temp_file_radoc.seek(0)

                    #if self.is_pdf(temp_file_radoc.name):
                    #    temp_file_radoc = PdfReader(temp_file_radoc)
                    #    output_pdf.append_pages_from_reader(temp_file_radoc)
                    #else:
                    #    return Util.response_bad_request(f'Erro da API: O RADOC de id {id} gerado não é um arquivo PDF válido.')
                    documentos_comprobatorios = DocumentoComprobatorio.objects.filter(relatorio_id=relatorio_id)
                    for documento in documentos_comprobatorios:
                        binary_data = documento.binary_pdf
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file_doc:
                            temp_file_doc.write(binary_data)
                            temp_file_doc.seek(0)

                            if not self.is_pdf(temp_file_doc.name):
                                return Util.response_bad_request(f'Erro: O documento comprobatório {temp_file_doc.name} não é um arquivo PDF válido.')
                                        
                            temp_file_doc = PdfReader(temp_file_doc)
                            output_pdf.append_pages_from_reader(temp_file_doc)
                           
                    with tempfile.NamedTemporaryFile(delete=False) as merged_file:
                        output_pdf.write(merged_file)
                        merged_file.seek(0)
                        
                        # Retorna o arquivo PDF diretamente como resposta
                        response = HttpResponse(merged_file, content_type='application/pdf')
                        response['Content-Disposition'] = f'inline; filename="Relatório Docente - UFRA"'
                        return response

            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em download_relatorio/{id}/')

class ExtrairDadosAtividadesLetivasPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        arquivo_pdf = request.FILES.get('pdf')

        if arquivo_pdf:
            try:
                texto_extraido = extrair_texto_do_pdf(arquivo_pdf)
                dados_extraidos = extrair_dados_de_atividades_letivas(texto_extraido)

                # Retorna os dados processados como parte da resposta
                return Response({'dados': dados_extraidos}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'erro': str(e + "não foi possível extrair os dados")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'erro': 'Nenhum arquivo PDF enviado.'}, status=status.HTTP_400_BAD_REQUEST)
 
class EndpointsView(APIView):
    def get(self, request):
        host = request.get_host()
        urls = get_resolver().reverse_dict.keys()
        return Response({"endpoints": [f"http://{host}/{url}" for url in urls if isinstance(url, str)]})

