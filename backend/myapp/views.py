import json
from django.utils import timezone
import tempfile
import os
from io import BytesIO
import subprocess
import fitz 
from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.extraction_strategy import PDFExtractionCoordinator
from myapp.serializer import (UsuarioSerializer, RelatorioDocenteSerializer, AtividadeLetivaSerializer, CalculoCHSemanalAulasSerializer, AtividadePedagogicaComplementarSerializer, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer, DescricaoOrientacaoCoorientacaoAcademicaSerializer, SupervisaoAcademicaSerializer, PreceptoriaTutoriaResidenciaSerializer, BancaExaminadoraSerializer, CHSemanalAtividadeEnsinoSerializer, AvaliacaoDiscenteSerializer, ProjetoPesquisaProducaoIntelectualSerializer, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer, LivroCapituloVerbetePublicadoSerializer, TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer, OutraAtividadePesquisaProducaoIntelectualSerializer, CHSemanalAtividadesPesquisaSerializer, ProjetoExtensaoSerializer, EstagioExtensaoSerializer, AtividadeEnsinoNaoFormalSerializer, OutraAtividadeExtensaoSerializer, CHSemanalAtividadesExtensaoSerializer, DistribuicaoCHSemanalSerializer, AtividadeGestaoRepresentacaoSerializer, QualificacaoDocenteAcademicaProfissionalSerializer, OutraInformacaoSerializer, AfastamentoSerializer, DocumentoComprobatorioSerializer, CustomizarTokenSerializer)
from .models import (Usuario, RelatorioDocente, AtividadeLetiva, CalculoCHSemanalAulas, AtividadePedagogicaComplementar, AtividadeOrientacaoSupervisaoPreceptoriaTutoria, DescricaoOrientacaoCoorientacaoAcademica, SupervisaoAcademica, PreceptoriaTutoriaResidencia, BancaExaminadora, CHSemanalAtividadeEnsino, AvaliacaoDiscente, ProjetoPesquisaProducaoIntelectual, TrabalhoCompletoPublicadoPeriodicoBoletimTecnico, LivroCapituloVerbetePublicado, TrabalhoCompletoResumoPublicadoApresentadoCongressos, OutraAtividadePesquisaProducaoIntelectual, CHSemanalAtividadesPesquisa, ProjetoExtensao, EstagioExtensao, AtividadeEnsinoNaoFormal, OutraAtividadeExtensao, CHSemanalAtividadesExtensao, DistribuicaoCHSemanal, AtividadeGestaoRepresentacao, QualificacaoDocenteAcademicaProfissional, OutraInformacao, Afastamento, DocumentoComprobatorio)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .services import extrair_texto_do_pdf, extrair_dados_de_atividades_letivas, escrever_dados_no_radoc
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

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
        usuario_autenticado = Usuario.objects.get(pk = request.user.id)
        old_username = usuario_autenticado.username
        old_email = usuario_autenticado.email
        
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
        if self.is_username_disponivel(new_username) == False and new_username != old_username:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
        if self.is_email_disponivel(new_email) == False and new_email != old_email:
            return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')
        
        serializer = UsuarioSerializer(instance, data=data, partial=True)

        if serializer.is_valid():
            usuario = serializer.save()
            if new_email and new_email != old_email:
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
            old_username = usuario_autenticado.username
            old_email = usuario_autenticado.email

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
                if self.is_username_disponivel(new_username) == False and new_username != old_username:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
                if self.is_email_disponivel(new_email) == False and new_email != old_email:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')

                serializer = UsuarioSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    usuario = serializer.save()
                    if new_email and new_email != old_email:
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
        login = request.data.get('login', None)
        password = request.data.get('password', None)

        if login and password:
            return self.getToken(login, password)
        return Util.response_unauthorized('É necessário fornecer login e senha para logar.')

    def getToken(self, login, password):
        usuario = None
        try:
            usuario = Usuario.objects.get(email=login)
        except Usuario.DoesNotExist:
            try:
                usuario = Usuario.objects.get(username=login)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não existe nenhum usuário cadastrado com esse e-mail ou username.')

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
        
        #origin = "http://localhost:4200"
        origin = "https://9ffa-2804-1b2-d082-593a-8156-5713-b520-7a8e.ngrok-free.app"
        return redirect(f'{origin}/login/?ativacao_sucesso=true')

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
                            return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas Atividades Pedagógicas Complementares para cada Relatório de Docência, sendo uma para cada semestre.')
                        
                        for instance in instances:
                            if instance.semestre is 1 and request.data['semestre'] is 1:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma Atividade Pedagógica Complementar por semestre para cada Relatório de Docência')
                            if instance.semestre is 2 and request.data['semestre'] is 2:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma Atividade Pedagógica Complementar por semestre para cada Relatório de Docência.')
                            
                except AtividadePedagogicaComplementar.DoesNotExist:
                    pass

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadePedagogicaComplementarSerializer(data=request.data)
                if serializer.is_valid():
                    # try:
                    #     relatorio_id = serializer.validated_data.get('relatorio_id')
                    #     semestre = serializer.validated_data.get('semestre')

                    #     calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(relatorio_id=relatorio_id, semestre=semestre)
                        
                    #     ch_semanal_total = serializer.validated_data.get('ch_semanal_graduacao') + serializer.validated_data.get('ch_semanal_pos_graduacao')

                    #     if ch_semanal_total > 2 * calculo_ch_semanal_aulas.ch_semanal_total:
                    #         return Util.response_bad_request('ERRO: não é possível criar uma atividade_pedagogica_complementar em que a soma entre ch_semanal_graduacao e ch_semanal_pos_graduacao seja maior que o dobro do ch_semanal_total do seu calculo_ch_semanal_aulas correspondente')

                    # except CalculoCHSemanalAulas.DoesNotExist:
                    #     return Util.response_bad_request('ERRO: não é possível criar uma atividade_pedagogica_complementar para um semestre em específico sem antes criar uma Atividade Letiva para o mesmo semestre.')
            
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

                    #Lógica DELETE ch_semanal_atividade_ensino
                    ch_semanal_atividade_ensino = None

                    try:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_docente.pk)

                        if atividade_pedagogica_complementar.semestre == 1:
                            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - atividade_pedagogica_complementar.ch_semanal_total
                        else:
                            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - atividade_pedagogica_complementar.ch_semanal_total

                    except CHSemanalAtividadeEnsino.DoesNotExist:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                        relatorio_id = relatorio_docente.pk,
                        ch_semanal_primeiro_semestre = 0.0,
                        ch_semanal_segundo_semestre = 0.0
                    )
                    ch_semanal_atividade_ensino.save()
                    #Termina aqui

                    atividade_pedagogica_complementar.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                except AtividadePedagogicaComplementar.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um atividade_pedagogica_complementar com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja deletar em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma atividade_pedagogica_complementar em atividade_pedagogica_complementar/{nome_relatorio}/{id_atividade_pedagogica_complementar}/')

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

                    #Lógica DELETE ch_semanal_atividade_ensino
                    ch_semanal_atividade_ensino = None

                    try:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_docente.pk)

                        if atividade_orientacao_supervisao_preceptoria_tutoria.semestre == 1:
                            ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - atividade_orientacao_supervisao_preceptoria_tutoria.ch_semanal_total
                        else:
                            ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - atividade_orientacao_supervisao_preceptoria_tutoria.ch_semanal_total

                    except CHSemanalAtividadeEnsino.DoesNotExist:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                        relatorio_id = relatorio_docente.pk,
                        ch_semanal_primeiro_semestre = 0.0,
                        ch_semanal_segundo_semestre = 0.0
                    )
                    ch_semanal_atividade_ensino.save()
                    #Termina aqui

                    atividade_orientacao_supervisao_preceptoria_tutoria.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da atividade_orientacao_supervisao_preceptoria_tutoria que você deseja deletar em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma atividade_orientacao_supervisao_preceptoria_tutoria em atividade_orientacao_supervisao_preceptoria_tutoria/{nome_relatorio}/{id_atividade_orientacao_supervisao_preceptoria_tutoria}/')
        
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
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma descricao_orientacao_coorientacao_academica em descricao_orientacao_coorientacao_academica/{nome_relatorio}/{id_descricao_orientacao_coorientacao_academica}/')
    
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
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma supervisao_academica em supervisao_academica/{nome_relatorio}/{id_supervisao_academica}/')
        

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
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma preceptoria_tutoria_residencia em preceptoria_tutoria_residencia/{nome_relatorio}/{id_preceptoria_tutoria_residencia}/')

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

                    #Lógica DELETE ch_semanal_atividade_ensino
                    ch_semanal_atividade_ensino = None

                    try:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id = relatorio_docente.pk)

                        ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - banca_examinadora.ch_semanal_primeiro_semestre

                        ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - banca_examinadora.ch_semanal_segundo_semestre

                    except CHSemanalAtividadeEnsino.DoesNotExist:
                        ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                        relatorio_id = relatorio_docente.pk,
                        ch_semanal_primeiro_semestre = 0.0,
                        ch_semanal_segundo_semestre = 0.0
                    )
                        
                    ch_semanal_atividade_ensino.save()
                    #Termina aqui

                    banca_examinadora.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except BancaExaminadora.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da banca_examinadora que você deseja deletar em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma banca_examinadora em banca_examinadora/{nome_relatorio}/{id_banca_examinadora}/')

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
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma avaliacao_discente em avaliacao_discente/{nome_relatorio}/{id_avaliacao_discente}/')
    

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
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar um projeto_pesquisa_producao_intelectual em projeto_pesquisa_producao_intelectual/{nome_relatorio}/')

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
                    return Util.response_not_found('Não foi possível encontrar um projeto_pesquisa_producao_intelectual com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id do projeto_pesquisa_producao_intelectual que você deseja atualizar em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')
        
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
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um projeto_pesquisa_producao_intelectual em projeto_pesquisa_producao_intelectual/{nome_relatorio}/{id_projeto_pesquisa_producao_intelectual}/')


class TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_trabalho_completo_publicado_periodico_boletim_tecnico=None):
        if nome_relatorio and id_trabalho_completo_publicado_periodico_boletim_tecnico:
            return self.getById(request, nome_relatorio, id_trabalho_completo_publicado_periodico_boletim_tecnico)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_trabalho_completo_publicado_periodico_boletim_tecnico=None):
        if nome_relatorio:
            if id_trabalho_completo_publicado_periodico_boletim_tecnico:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(relatorio_id=relatorio_docente.pk, pk=id_trabalho_completo_publicado_periodico_boletim_tecnico)
                    serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_publicado_periodico_boletim_tecnico que você deseja ler em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{id_trabalho_completo_publicado_periodico_boletim_tecnico}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os trabalho_completo_publicado_periodico_boletim_tecnicos em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{trabalho_completo_publicado_periodico_boletim_tecnico}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as trabalho_completo_publicado_periodico_boletim_tecnico em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(data=request.data)
                if serializer.is_valid():
                    trabalho_completo_publicado_periodico_boletim_tecnico = serializer.save()
                    return Util.response_created(f'id: {trabalho_completo_publicado_periodico_boletim_tecnico.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma trabalho_completo_publicado_periodico_boletim_tecnico em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_trabalho_completo_publicado_periodico_boletim_tecnico=None):
        if nome_relatorio:
            if id_trabalho_completo_publicado_periodico_boletim_tecnico:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    trabalho_completo_publicado_periodico_boletim_tecnico = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(pk=id_trabalho_completo_publicado_periodico_boletim_tecnico, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer(trabalho_completo_publicado_periodico_boletim_tecnico, data=data, partial=True)
                    if serializer.is_valid():
                        trabalho_completo_publicado_periodico_boletim_tecnico = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_publicado_periodico_boletim_tecnico que você deseja atualizar em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{id_trabalho_completo_publicado_periodico_boletim_tecnico}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma trabalho_completo_publicado_periodico_boletim_tecnico em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{id_trabalho_completo_publicado_periodico_boletim_tecnico}/')
    
    def delete(self, request, nome_relatorio=None, id_trabalho_completo_publicado_periodico_boletim_tecnico=None):
        if nome_relatorio:
            if id_trabalho_completo_publicado_periodico_boletim_tecnico:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    trabalho_completo_publicado_periodico_boletim_tecnico = TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.get(pk=id_trabalho_completo_publicado_periodico_boletim_tecnico, relatorio_id = relatorio_docente.pk)
                    trabalho_completo_publicado_periodico_boletim_tecnico.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_publicado_periodico_boletim_tecnico que você deseja deletar em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{id_trabalho_completo_publicado_periodico_boletim_tecnico}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um trabalho_completo_publicado_periodico_boletim_tecnico em trabalho_completo_publicado_periodico_boletim_tecnico/{nome_relatorio}/{id_trabalho_completo_publicado_periodico_boletim_tecnico}/')

class LivroCapituloVerbetePublicadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_livro_capitulo_verbete_publicado=None):
        if nome_relatorio and id_livro_capitulo_verbete_publicado:
            return self.getById(request, nome_relatorio, id_livro_capitulo_verbete_publicado)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_livro_capitulo_verbete_publicado=None):
        if nome_relatorio:
            if id_livro_capitulo_verbete_publicado:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = LivroCapituloVerbetePublicado.objects.get(relatorio_id=relatorio_docente.pk, pk=id_livro_capitulo_verbete_publicado)
                    serializer = LivroCapituloVerbetePublicadoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except LivroCapituloVerbetePublicado.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma livro_capitulo_verbete_publicado com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da livro_capitulo_verbete_publicado que você deseja ler em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as livro_capitulo_verbete_publicado em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = LivroCapituloVerbetePublicado.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = LivroCapituloVerbetePublicadoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as livro_capitulo_verbete_publicado em livro_capitulo_verbete_publicado/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = LivroCapituloVerbetePublicadoSerializer(data=request.data)
                if serializer.is_valid():
                    livro_capitulo_verbete_publicado = serializer.save()
                    return Util.response_created(f'id: {livro_capitulo_verbete_publicado.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma livro_capitulo_verbete_publicado em livro_capitulo_verbete_publicado/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_livro_capitulo_verbete_publicado=None):
        if nome_relatorio:
            if id_livro_capitulo_verbete_publicado:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    livro_capitulo_verbete_publicado = LivroCapituloVerbetePublicado.objects.get(pk=id_livro_capitulo_verbete_publicado, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = LivroCapituloVerbetePublicadoSerializer(livro_capitulo_verbete_publicado, data=data, partial=True)
                    if serializer.is_valid():
                        livro_capitulo_verbete_publicado = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except LivroCapituloVerbetePublicado.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma livro_capitulo_verbete_publicado com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da livro_capitulo_verbete_publicado que você deseja atualizar em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma livro_capitulo_verbete_publicado em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')
    
    def delete(self, request, nome_relatorio=None, id_livro_capitulo_verbete_publicado=None):
        if nome_relatorio:
            if id_livro_capitulo_verbete_publicado:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    livro_capitulo_verbete_publicado = LivroCapituloVerbetePublicado.objects.get(pk=id_livro_capitulo_verbete_publicado, relatorio_id = relatorio_docente.pk)
                    livro_capitulo_verbete_publicado.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except LivroCapituloVerbetePublicado.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma livro_capitulo_verbete_publicado com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da livro_capitulo_verbete_publicado que você deseja deletar em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um livro_capitulo_verbete_publicado em livro_capitulo_verbete_publicado/{nome_relatorio}/{id_livro_capitulo_verbete_publicado}/')

class TrabalhoCompletoResumoPublicadoApresentadoCongressosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_trabalho_completo_resumo_publicado_apresentado_congressos=None):
        if nome_relatorio and id_trabalho_completo_resumo_publicado_apresentado_congressos:
            return self.getById(request, nome_relatorio, id_trabalho_completo_resumo_publicado_apresentado_congressos)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_trabalho_completo_resumo_publicado_apresentado_congressos=None):
        if nome_relatorio:
            if id_trabalho_completo_resumo_publicado_apresentado_congressos:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(relatorio_id=relatorio_docente.pk, pk=id_trabalho_completo_resumo_publicado_apresentado_congressos)
                    serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_resumo_publicado_apresentado_congressos com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_resumo_publicado_apresentado_congressos que você deseja ler em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as trabalho_completo_resumo_publicado_apresentado_congressos em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as trabalho_completo_resumo_publicado_apresentado_congressos em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(data=request.data)
                if serializer.is_valid():
                    trabalho_completo_resumo_publicado_apresentado_congressos = serializer.save()
                    return Util.response_created(f'id: {trabalho_completo_resumo_publicado_apresentado_congressos.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma trabalho_completo_resumo_publicado_apresentado_congressos em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_trabalho_completo_resumo_publicado_apresentado_congressos=None):
        if nome_relatorio:
            if id_trabalho_completo_resumo_publicado_apresentado_congressos:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    trabalho_completo_resumo_publicado_apresentado_congressos = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(pk=id_trabalho_completo_resumo_publicado_apresentado_congressos, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer(trabalho_completo_resumo_publicado_apresentado_congressos, data=data, partial=True)
                    if serializer.is_valid():
                        trabalho_completo_resumo_publicado_apresentado_congressos = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_publicado_periodico_boletim_tecnico com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_publicado_periodico_boletim_tecnico que você deseja atualizar em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma trabalho_completo_resumo_publicado_apresentado_congressos em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')
    
    def delete(self, request, nome_relatorio=None, id_trabalho_completo_resumo_publicado_apresentado_congressos=None):
        if nome_relatorio:
            if id_trabalho_completo_resumo_publicado_apresentado_congressos:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    trabalho_completo_resumo_publicado_apresentado_congressos = TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.get(pk=id_trabalho_completo_resumo_publicado_apresentado_congressos, relatorio_id = relatorio_docente.pk)
                    trabalho_completo_resumo_publicado_apresentado_congressos.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except TrabalhoCompletoResumoPublicadoApresentadoCongressos.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma trabalho_completo_resumo_publicado_apresentado_congressos com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da trabalho_completo_resumo_publicado_apresentado_congressos que você deseja deletar em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um trabalho_completo_resumo_publicado_apresentado_congressos em trabalho_completo_resumo_publicado_apresentado_congressos/{nome_relatorio}/{id_trabalho_completo_resumo_publicado_apresentado_congressos}/')
    

class OutraAtividadePesquisaProducaoIntelectualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_outra_atividade_pesquisa_producao_intelectual=None):
        if nome_relatorio and id_outra_atividade_pesquisa_producao_intelectual:
            return self.getById(request, nome_relatorio, id_outra_atividade_pesquisa_producao_intelectual)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_outra_atividade_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_outra_atividade_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = OutraAtividadePesquisaProducaoIntelectual.objects.get(relatorio_id=relatorio_docente.pk, pk=id_outra_atividade_pesquisa_producao_intelectual)
                    serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_pesquisa_producao_intelectual que você deseja ler em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os outra_atividade_pesquisa_producao_intelectual em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = OutraAtividadePesquisaProducaoIntelectual.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as outra_atividade_pesquisa_producao_intelectual em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(data=request.data)
                if serializer.is_valid():
                    outra_atividade_pesquisa_producao_intelectual = serializer.save()
                    return Util.response_created(f'id: {outra_atividade_pesquisa_producao_intelectual.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma outra_atividade_pesquisa_producao_intelectual em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_outra_atividade_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_outra_atividade_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    outra_atividade_pesquisa_producao_intelectual = OutraAtividadePesquisaProducaoIntelectual.objects.get(pk=id_outra_atividade_pesquisa_producao_intelectual, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = OutraAtividadePesquisaProducaoIntelectualSerializer(outra_atividade_pesquisa_producao_intelectual, data=data, partial=True)
                    if serializer.is_valid():
                        outra_atividade_pesquisa_producao_intelectual = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_pesquisa_producao_intelectualo que você deseja atualizar em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma outra_atividade_pesquisa_producao_intelectual em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')
   
    def delete(self, request, nome_relatorio=None, id_outra_atividade_pesquisa_producao_intelectual=None):
        if nome_relatorio:
            if id_outra_atividade_pesquisa_producao_intelectual:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    outra_atividade_pesquisa_producao_intelectual = OutraAtividadePesquisaProducaoIntelectual.objects.get(pk=id_outra_atividade_pesquisa_producao_intelectual, relatorio_id = relatorio_docente.pk)
                    outra_atividade_pesquisa_producao_intelectual.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except OutraAtividadePesquisaProducaoIntelectual.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_pesquisa_producao_intelectual com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_pesquisa_producao_intelectual que você deseja deletar em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma outra_atividade_pesquisa_producao_intelectual em outra_atividade_pesquisa_producao_intelectual/{nome_relatorio}/{id_outra_atividade_pesquisa_producao_intelectual}/')


class CHSemanalAtividadesPesquisaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_ch_semanal_atividades_pesquisa=None):
        if nome_relatorio and id_ch_semanal_atividades_pesquisa:
            return self.getById(request, nome_relatorio, id_ch_semanal_atividades_pesquisa)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_ch_semanal_atividades_pesquisa=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_pesquisa:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = CHSemanalAtividadesPesquisa.objects.get(relatorio_id=relatorio_docente.pk, pk=id_ch_semanal_atividades_pesquisa)
                    serializer = CHSemanalAtividadesPesquisaSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
            
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except CHSemanalAtividadesPesquisa.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido.')
            
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_pesquisa que você deseja ler em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as chs_semanais_atividades_pesquisas em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = CHSemanalAtividadesPesquisa.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = CHSemanalAtividadesPesquisaSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as chs_semanais_atividades_pesquisas em ch_semanal_atividades_pesquisa/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = CHSemanalAtividadesPesquisaSerializer(data=request.data)
                if serializer.is_valid():
                    relatorio_id = serializer.validated_data.get('relatorio_id')
                    try:
                        instances = CHSemanalAtividadesPesquisa.objects.filter(relatorio_id=relatorio_id)
                        if instances.count() > 0:
                            if instances.count() == 1:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma ch_semanal_atividades_pesquisa para cada relatorio_docente.')
                            
                    except CHSemanalAtividadesPesquisa.DoesNotExist:
                        pass

                    ch_semanal_atividades_pesquisa = serializer.save()
                    return Util.response_created(f'id: {ch_semanal_atividades_pesquisa.pk}')
                return Util.response_bad_request(serializer.errors)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma ch_semanal_atividades_pesquisa em ch_semanal_atividades_pesquisa/{nome_relatorio}/')
    
    def put(self, request, nome_relatorio=None, id_ch_semanal_atividades_pesquisa=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_pesquisa:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    ch_semanal_atividades_pesquisa = CHSemanalAtividadesPesquisa.objects.get(pk=id_ch_semanal_atividades_pesquisa, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = CHSemanalAtividadesPesquisaSerializer(ch_semanal_atividades_pesquisa, data=data, partial=True)
                    if serializer.is_valid():
                        ch_semanal_atividades_pesquisa = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                    
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except CHSemanalAtividadesPesquisa.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_pesquisa que você deseja atualizar em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma ch_semanal_atividades_pesquisa em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')
    

    def delete(self, request, nome_relatorio=None, id_ch_semanal_atividades_pesquisa=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_pesquisa:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                    ch_semanal_atividades_pesquisa = CHSemanalAtividadesPesquisa.objects.get(pk=id_ch_semanal_atividades_pesquisa, relatorio_id = relatorio_docente.pk)

                    ch_semanal_atividades_pesquisa.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
                
                except CHSemanalAtividadesPesquisa.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_pesquisa com o id fornecido.')
                
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_pesquisa que você deseja deletar em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma ch_semanal_atividades_pesquisa em ch_semanal_atividades_pesquisa/{nome_relatorio}/{id_ch_semanal_atividades_pesquisa}/')
    
        
class ProjetoExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_projeto_extensao=None):
        if nome_relatorio and id_projeto_extensao:
            return self.getById(request, nome_relatorio, id_projeto_extensao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_projeto_extensao=None):
        if nome_relatorio:
            if id_projeto_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = ProjetoExtensao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_projeto_extensao)
                    serializer = ProjetoExtensaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except ProjetoExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma projeto_extensao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da projeto_extensao que você deseja ler em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os projeto_extensao em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = ProjetoExtensao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = ProjetoExtensaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as projeto_extensao em projeto_extensao/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = ProjetoExtensaoSerializer(data=request.data)
                if serializer.is_valid():
                    projeto_extensao = serializer.save()
                    return Util.response_created(f'id: {projeto_extensao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma projeto_extensao em projeto_extensao/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_projeto_extensao=None):
        if nome_relatorio:
            if id_projeto_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    projeto_extensao = ProjetoExtensao.objects.get(pk=id_projeto_extensao, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = ProjetoExtensaoSerializer(projeto_extensao, data=data, partial=True)
                    if serializer.is_valid():
                        projeto_extensao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except ProjetoExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma projeto_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da projeto_extensaoo que você deseja atualizar em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma projeto_extensao em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')
   
    def delete(self, request, nome_relatorio=None, id_projeto_extensao=None):
        if nome_relatorio:
            if id_projeto_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    projeto_extensao = ProjetoExtensao.objects.get(pk=id_projeto_extensao, relatorio_id = relatorio_docente.pk)
                    projeto_extensao.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except ProjetoExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um projeto_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do projeto_extensao que você deseja deletar em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um projeto_extensao em projeto_extensao/{nome_relatorio}/{id_projeto_extensao}/')

        
class EstagioExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_estagio_extensao=None):
        if nome_relatorio and id_estagio_extensao:
            return self.getById(request, nome_relatorio, id_estagio_extensao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_estagio_extensao=None):
        if nome_relatorio:
            if id_estagio_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = EstagioExtensao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_estagio_extensao)
                    serializer = EstagioExtensaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except EstagioExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma estagio_extensao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da estagio_extensao que você deseja ler em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os estagio_extensao em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = EstagioExtensao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = EstagioExtensaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as estagio_extensao em estagio_extensao/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = EstagioExtensaoSerializer(data=request.data)
                if serializer.is_valid():
                    estagio_extensao = serializer.save()
                    return Util.response_created(f'id: {estagio_extensao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma estagio_extensao em estagio_extensao/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_estagio_extensao=None):
        if nome_relatorio:
            if id_estagio_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)
                    estagio_extensao = EstagioExtensao.objects.get(pk=id_estagio_extensao, relatorio_id = relatorio_docente.pk)
                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = EstagioExtensaoSerializer(estagio_extensao, data=data, partial=True)
                    if serializer.is_valid():
                        estagio_extensao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except EstagioExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um estagio_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da estagio_extensao que você deseja atualizar em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma estagio_extensao em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')
   
    def delete(self, request, nome_relatorio=None, id_estagio_extensao=None):
        if nome_relatorio:
            if id_estagio_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    estagio_extensao = EstagioExtensao.objects.get(pk=id_estagio_extensao, relatorio_id = relatorio_docente.pk)
                    estagio_extensao.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except EstagioExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um estagio_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do estagio_extensao que você deseja deletar em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um estagio_extensao em estagio_extensao/{nome_relatorio}/{id_estagio_extensao}/')

        
class AtividadeEnsinoNaoFormalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_atividade_ensino_nao_formal=None):
        if nome_relatorio and id_atividade_ensino_nao_formal:
            return self.getById(request, nome_relatorio, id_atividade_ensino_nao_formal)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_atividade_ensino_nao_formal=None):
        if nome_relatorio:
            if id_atividade_ensino_nao_formal:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = AtividadeEnsinoNaoFormal.objects.get(relatorio_id=relatorio_docente.pk, pk=id_atividade_ensino_nao_formal)
                    serializer = AtividadeEnsinoNaoFormalSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except AtividadeEnsinoNaoFormal.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da atividade_ensino_nao_formal que você deseja ler em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os atividade_ensino_nao_formal em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AtividadeEnsinoNaoFormal.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AtividadeEnsinoNaoFormalSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as atividade_ensino_nao_formal em atividade_ensino_nao_formal/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadeEnsinoNaoFormalSerializer(data=request.data)
                if serializer.is_valid():
                    atividade_ensino_nao_formal = serializer.save()
                    return Util.response_created(f'id: {atividade_ensino_nao_formal.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma atividade_ensino_nao_formal em atividade_ensino_nao_formal/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_atividade_ensino_nao_formal=None):
        if nome_relatorio:
            if id_atividade_ensino_nao_formal:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    atividade_ensino_nao_formal = AtividadeEnsinoNaoFormal.objects.get(pk=id_atividade_ensino_nao_formal, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = AtividadeEnsinoNaoFormalSerializer(atividade_ensino_nao_formal, data=data, partial=True)
                    if serializer.is_valid():
                        atividade_ensino_nao_formal = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except AtividadeEnsinoNaoFormal.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da atividade_ensino_nao_formalo que você deseja atualizar em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma atividade_ensino_nao_formal em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')
   
    def delete(self, request, nome_relatorio=None, id_atividade_ensino_nao_formal=None):
        if nome_relatorio:
            if id_atividade_ensino_nao_formal:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    atividade_ensino_nao_formal = AtividadeEnsinoNaoFormal.objects.get(pk=id_atividade_ensino_nao_formal, relatorio_id = relatorio_docente.pk)
                    atividade_ensino_nao_formal.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except AtividadeEnsinoNaoFormal.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_ensino_nao_formal com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da atividade_ensino_nao_formal que você deseja deletar em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma atividade_ensino_nao_formal em atividade_ensino_nao_formal/{nome_relatorio}/{id_atividade_ensino_nao_formal}/')
    

class OutraAtividadeExtensaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_outra_atividade_extensao=None):
        if nome_relatorio and id_outra_atividade_extensao:
            return self.getById(request, nome_relatorio, id_outra_atividade_extensao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_outra_atividade_extensao=None):
        if nome_relatorio:
            if id_outra_atividade_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = OutraAtividadeExtensao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_outra_atividade_extensao)
                    serializer = OutraAtividadeExtensaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except OutraAtividadeExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_extensao que você deseja ler em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os outra_atividade_extensao em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = OutraAtividadeExtensao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = OutraAtividadeExtensaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as outra_atividade_extensao em outra_atividade_extensao/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = OutraAtividadeExtensaoSerializer(data=request.data)
                if serializer.is_valid():
                    outra_atividade_extensao = serializer.save()
                    return Util.response_created(f'id: {outra_atividade_extensao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma outra_atividade_extensao em outra_atividade_extensao/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_outra_atividade_extensao=None):
        if nome_relatorio:
            if id_outra_atividade_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    outra_atividade_extensao = OutraAtividadeExtensao.objects.get(pk=id_outra_atividade_extensao, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = OutraAtividadeExtensaoSerializer(outra_atividade_extensao, data=data, partial=True)
                    if serializer.is_valid():
                        outra_atividade_extensao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except OutraAtividadeExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_extensaoo que você deseja atualizar em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma outra_atividade_extensao em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')
   
    def delete(self, request, nome_relatorio=None, id_outra_atividade_extensao=None):
        if nome_relatorio:
            if id_outra_atividade_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    outra_atividade_extensao = OutraAtividadeExtensao.objects.get(pk=id_outra_atividade_extensao, relatorio_id = relatorio_docente.pk)
                    outra_atividade_extensao.delete()
                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except OutraAtividadeExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_atividade_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_atividade_extensao que você deseja deletar em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma outra_atividade_extensao em outra_atividade_extensao/{nome_relatorio}/{id_outra_atividade_extensao}/')

    
class CHSemanalAtividadesExtensaoView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request, nome_relatorio=None, id_ch_semanal_atividades_extensao=None):
        if nome_relatorio and id_ch_semanal_atividades_extensao:
            return self.getById(request, nome_relatorio, id_ch_semanal_atividades_extensao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_ch_semanal_atividades_extensao=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = CHSemanalAtividadesExtensao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_ch_semanal_atividades_extensao)
                    serializer = CHSemanalAtividadesExtensaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except CHSemanalAtividadesExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_extensao que você deseja ler em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler as ch_semanal_atividades_extensao em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
    
    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = CHSemanalAtividadesExtensao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = CHSemanalAtividadesExtensaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as chs_semanais_atividades_extensao em ch_semanal_atividades_extensao/{nome_relatorio}/')
    
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = CHSemanalAtividadesExtensaoSerializer(data=request.data)
                if serializer.is_valid():
                    relatorio_id = serializer.validated_data.get('relatorio_id')
                    try:
                        instances = CHSemanalAtividadesExtensao.objects.filter(relatorio_id=relatorio_id)
                        if instances.count() > 0:
                            if instances.count() == 1:
                                return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma ch_semanal_atividades_extensao para cada relatorio_docente.')

                    except CHSemanalAtividadesExtensao.DoesNotExist:
                        pass

                    ch_semanal_atividades_extensao = serializer.save()
                    return Util.response_created(f'id: {ch_semanal_atividades_extensao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma ch_semanal_atividades_extensao em ch_semanal_atividades_extensao/{nome_relatorio}/')
    
    
    def put(self, request, nome_relatorio=None, id_ch_semanal_atividades_extensao=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    ch_semanal_atividades_extensao = CHSemanalAtividadesExtensao.objects.get(pk=id_ch_semanal_atividades_extensao, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = CHSemanalAtividadesExtensaoSerializer(ch_semanal_atividades_extensao, data=data, partial=True)
                    if serializer.is_valid():
                        ch_semanal_atividades_extensao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except CHSemanalAtividadesExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_extensao que você deseja atualizar em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma ch_semanal_atividades_extensao em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
    
    def delete(self, request, nome_relatorio=None, id_ch_semanal_atividades_extensao=None):
        if nome_relatorio:
            if id_ch_semanal_atividades_extensao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    ch_semanal_atividades_extensao = CHSemanalAtividadesExtensao.objects.get(pk=id_ch_semanal_atividades_extensao, relatorio_id = relatorio_docente.pk)
                    ch_semanal_atividades_extensao.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except CHSemanalAtividadesExtensao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividades_extensao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da ch_semanal_atividades_extensao que você deseja deletar em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma ch_semanal_atividades_extensao em ch_semanal_atividades_extensao/{nome_relatorio}/{id_ch_semanal_atividades_extensao}/')
    
class AtividadeGestaoRepresentacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_atividade_gestao_representacao=None):
        if nome_relatorio and id_atividade_gestao_representacao:
            return self.getById(request, nome_relatorio, id_atividade_gestao_representacao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_atividade_gestao_representacao=None):
        if nome_relatorio:
            if id_atividade_gestao_representacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = AtividadeGestaoRepresentacao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_atividade_gestao_representacao)
                    serializer = AtividadeGestaoRepresentacaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except AtividadeGestaoRepresentacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da atividade_gestao_representacao que você deseja ler em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os atividade_gestao_representacao em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = AtividadeGestaoRepresentacao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AtividadeGestaoRepresentacaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as atividade_gestao_representacao em atividade_gestao_representacao/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AtividadeGestaoRepresentacaoSerializer(data=request.data)
                if serializer.is_valid():
                    atividade_gestao_representacao = serializer.save()
                    return Util.response_created(f'id: {atividade_gestao_representacao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma atividade_gestao_representacao em atividade_gestao_representacao/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_atividade_gestao_representacao=None):
        if nome_relatorio:
            if id_atividade_gestao_representacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    atividade_gestao_representacao = AtividadeGestaoRepresentacao.objects.get(pk=id_atividade_gestao_representacao, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = AtividadeGestaoRepresentacaoSerializer(atividade_gestao_representacao, data=data, partial=True)
                    if serializer.is_valid():
                        atividade_gestao_representacao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except AtividadeGestaoRepresentacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da atividade_gestao_representacaoo que você deseja atualizar em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma atividade_gestao_representacao em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')
   
    def delete(self, request, nome_relatorio=None, id_atividade_gestao_representacao=None):
        if nome_relatorio:
            if id_atividade_gestao_representacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    atividade_gestao_representacao = AtividadeGestaoRepresentacao.objects.get(pk=id_atividade_gestao_representacao, relatorio_id = relatorio_docente.pk)
                    atividade_gestao_representacao.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except AtividadeGestaoRepresentacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma atividade_gestao_representacao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da atividade_gestao_representacao que você deseja deletar em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma atividade_gestao_representacao em atividade_gestao_representacao/{nome_relatorio}/{id_atividade_gestao_representacao}/')
        
    
class QualificacaoDocenteAcademicaProfissionalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_qualificacao_docente_academica_profissional=None):
        if nome_relatorio and id_qualificacao_docente_academica_profissional:
            return self.getById(request, nome_relatorio, id_qualificacao_docente_academica_profissional)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_qualificacao_docente_academica_profissional=None):
        if nome_relatorio:
            if id_qualificacao_docente_academica_profissional:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = QualificacaoDocenteAcademicaProfissional.objects.get(relatorio_id=relatorio_docente.pk, pk=id_qualificacao_docente_academica_profissional)
                    serializer = QualificacaoDocenteAcademicaProfissionalSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da qualificacao_docente_academica_profissional que você deseja ler em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os qualificacao_docente_academica_profissional em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = QualificacaoDocenteAcademicaProfissional.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = QualificacaoDocenteAcademicaProfissionalSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as qualificacao_docente_academica_profissional em qualificacao_docente_academica_profissional/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)


                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = QualificacaoDocenteAcademicaProfissionalSerializer(data=request.data)
                if serializer.is_valid():
                    qualificacao_docente_academica_profissional = serializer.save()
                    return Util.response_created(f'id: {qualificacao_docente_academica_profissional.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma qualificacao_docente_academica_profissional em qualificacao_docente_academica_profissional/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_qualificacao_docente_academica_profissional=None):
        if nome_relatorio:
            if id_qualificacao_docente_academica_profissional:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    qualificacao_docente_academica_profissional = QualificacaoDocenteAcademicaProfissional.objects.get(pk=id_qualificacao_docente_academica_profissional, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = QualificacaoDocenteAcademicaProfissionalSerializer(qualificacao_docente_academica_profissional, data=data, partial=True)
                    if serializer.is_valid():
                        qualificacao_docente_academica_profissional = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da qualificacao_docente_academica_profissionalo que você deseja atualizar em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma qualificacao_docente_academica_profissional em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')
   
    def delete(self, request, nome_relatorio=None, id_qualificacao_docente_academica_profissional=None):
        if nome_relatorio:
            if id_qualificacao_docente_academica_profissional:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    qualificacao_docente_academica_profissional = QualificacaoDocenteAcademicaProfissional.objects.get(pk=id_qualificacao_docente_academica_profissional, relatorio_id = relatorio_docente.pk)
                    qualificacao_docente_academica_profissional.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except QualificacaoDocenteAcademicaProfissional.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma qualificacao_docente_academica_profissional com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da qualificacao_docente_academica_profissional que você deseja deletar em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma qualificacao_docente_academica_profissional em qualificacao_docente_academica_profissional/{nome_relatorio}/{id_qualificacao_docente_academica_profissional}/')

    
class OutraInformacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_outra_informacao=None):
        if nome_relatorio and id_outra_informacao:
            return self.getById(request, nome_relatorio, id_outra_informacao)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_outra_informacao=None):
        if nome_relatorio:
            if id_outra_informacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = OutraInformacao.objects.get(relatorio_id=relatorio_docente.pk, pk=id_outra_informacao)
                    serializer = OutraInformacaoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except OutraInformacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da outra_informacao que você deseja ler em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os outra_informacao em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')


    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = OutraInformacao.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = OutraInformacaoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as outra_informacao em outra_informacao/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = OutraInformacaoSerializer(data=request.data)
                if serializer.is_valid():
                    outra_informacao = serializer.save()
                    return Util.response_created(f'id: {outra_informacao.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma outra_informacao em outra_informacao/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_outra_informacao=None):
        if nome_relatorio:
            if id_outra_informacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)


                    outra_informacao = OutraInformacao.objects.get(pk=id_outra_informacao, relatorio_id = relatorio_docente.pk)


                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')


                    serializer = OutraInformacaoSerializer(outra_informacao, data=data, partial=True)
                    if serializer.is_valid():
                        outra_informacao = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except OutraInformacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_informacaoo que você deseja atualizar em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar uma outra_informacao em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')
   
    def delete(self, request, nome_relatorio=None, id_outra_informacao=None):
        if nome_relatorio:
            if id_outra_informacao:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    outra_informacao = OutraInformacao.objects.get(pk=id_outra_informacao, relatorio_id = relatorio_docente.pk)
                    outra_informacao.delete()


                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except OutraInformacao.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma outra_informacao com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id da outra_informacao que você deseja deletar em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar uma outra_informacao em outra_informacao/{nome_relatorio}/{id_outra_informacao}/')
    
    
class AfastamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_afastamento=None):
        if nome_relatorio and id_afastamento:
            return self.getById(request, nome_relatorio, id_afastamento)
        else:
            return self.getAll(request, nome_relatorio)
       
    def getById(self, request, nome_relatorio=None, id_afastamento=None):
        if nome_relatorio:
            if id_afastamento:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = Afastamento.objects.get(relatorio_id=relatorio_docente.pk, pk=id_afastamento)
                    serializer = AfastamentoSerializer(instance)
                    return Util.response_ok_no_message(serializer.data)
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')


                except Afastamento.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma afastamento com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id da afastamento que você deseja ler em afastamento/{nome_relatorio}/{id_afastamento}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler os afastamento em afastamento/{nome_relatorio}/{id_afastamento}/')

    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = Afastamento.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = AfastamentoSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler as afastamento em afastamento/{nome_relatorio}/')
   
    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = AfastamentoSerializer(data=request.data)
                if serializer.is_valid():
                    afastamento = serializer.save()
                    return Util.response_created(f'id: {afastamento.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar uma afastamento em afastamento/{nome_relatorio}/')
   
    def put(self, request, nome_relatorio=None, id_afastamento=None):
        if nome_relatorio:
            if id_afastamento:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    afastamento = Afastamento.objects.get(pk=id_afastamento, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = AfastamentoSerializer(afastamento, data=data, partial=True)
                    if serializer.is_valid():
                        afastamento = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except Afastamento.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma afastamento com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do afastamento que você deseja atualizar em afastamento/{nome_relatorio}/{id_afastamento}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar um afastamento em afastamento/{nome_relatorio}/{id_afastamento}/')
   
    def delete(self, request, nome_relatorio=None, id_afastamento=None):
        if nome_relatorio:
            if id_afastamento:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    afastamento = Afastamento.objects.get(pk=id_afastamento, relatorio_id = relatorio_docente.pk)
                    afastamento.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except Afastamento.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar uma afastamento com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do afastamento que você deseja deletar em afastamento/{nome_relatorio}/{id_afastamento}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um afastamento em afastamento/{nome_relatorio}/{id_afastamento}/')

    
class DocumentoComprobatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nome_relatorio=None, id_documento_comprobatorio=None):
        if nome_relatorio and id_documento_comprobatorio:
            return self.getById(request, nome_relatorio, id_documento_comprobatorio)
        else:
            return self.getAll(request, nome_relatorio)
        
    def getById(self, request, nome_relatorio=None, id_documento_comprobatorio=None):
        if nome_relatorio:
            if id_documento_comprobatorio:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                    instance = DocumentoComprobatorio.objects.get(relatorio_id=relatorio_docente.pk, pk=id_documento_comprobatorio)

                    binary_data = instance.binary_pdf
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(binary_data)
                        temp_file.seek(0)

                        # Retorna o arquivo PDF diretamente como resposta
                        response = HttpResponse(temp_file, content_type='application/pdf')
                        response['Content-Disposition'] = f'inline; filename="{temp_file.name}"'
                        return response
           
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except DocumentoComprobatorio.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido.')
           
            return Util.response_bad_request('É necessário fornecer o id do documento_comprobatorio que você deseja ler em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja deseja ler um documento_comprobatorio em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
    
    def getAll(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome=nome_relatorio)
                instances = DocumentoComprobatorio.objects.filter(relatorio_id=relatorio_docente.pk)
                serializer = DocumentoComprobatorioSerializer(instances, many=True)
                return Util.response_ok_no_message(serializer.data)
           
            except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente do qual você deseja ler os documentos_comprobatorios em documento_comprobatorio/{nome_relatorio}/')

    def post(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)

                request.data['relatorio_id'] = relatorio_docente.pk
                serializer = DocumentoComprobatorioSerializer(data=request.data)
                if serializer.is_valid():
                    documento_comprobatorio = serializer.save()
                    return Util.response_created(f'id: {documento_comprobatorio.pk}')
                return Util.response_bad_request(serializer.errors)
           
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
           
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja criar um documento_comprobatorio em documento_comprobatorio/{nome_relatorio}/')

    def put(self, request, nome_relatorio=None, id_documento_comprobatorio=None):
        if nome_relatorio:
            if id_documento_comprobatorio:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                    documento_comprobatorio = DocumentoComprobatorio.objects.get(pk=id_documento_comprobatorio, relatorio_id = relatorio_docente.pk)

                    data = request.data.copy()
                    if 'id' in data or 'relatorio_id' in data:
                        return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                    serializer = DocumentoComprobatorioSerializer(documento_comprobatorio, data=data, partial=True)
                    if serializer.is_valid():
                        documento_comprobatorio = serializer.save()
                        return Util.response_ok_no_message(serializer.data)
                    else:
                        return Util.response_bad_request(serializer.errors)
                   
                except RelatorioDocente.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')

                except DocumentoComprobatorio.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do documento_comprobatorio que você deseja atualizar em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
       
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja atualizar um documento_comprobatorio em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
    

    def delete(self, request, nome_relatorio=None, id_documento_comprobatorio=None):
        if nome_relatorio:
            if id_documento_comprobatorio:
                try:
                    usuario_id = request.user.id
                    relatorio_docente = RelatorioDocente.objects.get(usuario_id=usuario_id, nome=nome_relatorio)
                    documento_comprobatorio = DocumentoComprobatorio.objects.get(pk=id_documento_comprobatorio, relatorio_id = relatorio_docente.pk)

                    documento_comprobatorio.delete()

                    return Util.response_ok_no_message('Objeto excluído com sucesso.')
               
                except DocumentoComprobatorio.DoesNotExist:
                    return Util.response_not_found('Não foi possível encontrar um documento_comprobatorio com o id fornecido.')
               
            return Util.response_bad_request('É necessário fornecer o id do documento_comprobatorio que você deseja deletar em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
        
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente no qual você deseja deletar um documento_comprobatorio em documento_comprobatorio/{nome_relatorio}/{id_documento_comprobatorio}/')
    

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
    
    def get(self, request, nome_relatorio=None):
        if nome_relatorio:
            return self.getOneByUser(request, nome_relatorio)
        else:
            return self.getAllByUser(request)
        
    def getAllByUser(self, request):
        instances = RelatorioDocente.objects.filter(usuario_id = request.user.id)
        serializer = RelatorioDocenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getOneByUser(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                instance = RelatorioDocente.objects.get(usuario_id = request.user.id, nome=nome_relatorio)
                serializer = RelatorioDocenteSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('O usuário não possui nenhum relatorio_docente com esse nome.')
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja ler.')
    
    def put(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                usuario_id = request.user.id
                relatorio_docente = RelatorioDocente.objects.get(usuario_id = usuario_id, nome = nome_relatorio)

                data = request.data.copy()
                if 'id' in data or 'usuario_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou usuario_id')

                serializer = RelatorioDocenteSerializer(relatorio_docente, data=data, partial=True)
                if serializer.is_valid():
                    relatorio_docente = serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)
                   
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido que seja pertencente ao usuário autenticado.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja atualizar em relatorio_docente/{nome_relatorio}/')

    
    def delete(self, request, nome_relatorio=None):
        if nome_relatorio:
            try:
                instance = RelatorioDocente.objects.get(usuario_id = request.user.id, nome=nome_relatorio)
                instance.delete()
                return Util.response_ok_no_message('RADOC excluído com sucesso.')
            
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma relatorio_docente pertencente ao usuário que tenha o nome fornecido.')
            
        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja deletar em relatorio_docente/{nome_relatorio}/')
    
    
class RelatorioDocenteAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, relatorio_id=None, username=None):
        if relatorio_id:
            return self.getById(request, relatorio_id)
        elif username:
            return self.getByUser(request, username)
        else:
            return self.getAll(request)
        
    def getAll(self, request):
        usuario_autenticado = Usuario.objects.get(pk = request.user.id)
        if usuario_autenticado.perfil != "Administrador":
            return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
        
        instances = RelatorioDocente.objects.all()
        serializer = RelatorioDocenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getByUser(self, request, username=None):
        if username:
            usuario = None
            try:
                usuario = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não existe nenhum usuário que possua esse id.')
                
            instances = RelatorioDocente.objects.filter(usuario_id = usuario.pk)
            serializer = RelatorioDocenteSerializer(instances, many=True)
            return Util.response_ok_no_message(serializer.data)
        
        return Util.response_bad_request('É necessário fornecer o id do usuário o qual você deseja obter os radocs criados em relatorio_docente/admin/usuario/{username}/')
    
    def getById(self, request, relatorio_id=None):
        if relatorio_id:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                instance = RelatorioDocente.objects.get(pk=relatorio_id)
                serializer = RelatorioDocenteSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em relatorio_docente/admin/{relatorio_id}/')
        
    def delete(self, request, relatorio_id=None):
        if relatorio_id:
            usuario_autenticado = Usuario.objects.get(pk = request.user.id)
            if usuario_autenticado.perfil != "Administrador":
                return Util.response_unauthorized("Apenas usuários administradores podem realizar essa requisição!")
            try:
                instance = RelatorioDocente.objects.get(pk=relatorio_id)
                instance.delete()
                return Util.response_ok_no_message('RADOC excluído com sucesso.')
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma relatorio_docente com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em relatorio_docente/admin/{relatorio_id}/')
    
class DownloadRelatorioDocenteView(APIView):
    permission_classes = [IsAuthenticated]

    def is_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)  # Tente abrir o arquivo como um PDF
            doc.close()  # Feche o arquivo
            return True  # Se abrir sem erros, é um PDF válido
        except Exception as e:
            return False
        
    def gerarPDFRadoc(self, relatorio_id, usuario_id):
        id = relatorio_id
        usuario_id = usuario_id
        usuario_dicts = [model_to_dict(usuario_obj) for usuario_obj in Usuario.objects.filter(id=usuario_id)]
        relatorio_docente_dicts = [model_to_dict(relatorio_obj) for relatorio_obj in RelatorioDocente.objects.filter(pk=id, usuario_id=usuario_id)]
        atividade_letiva_dicts = [model_to_dict(atividade_obj) for atividade_obj in AtividadeLetiva.objects.filter(relatorio_id=id)]
        calculo_ch_semanal_aulas_dicts = [model_to_dict(calculo_ch_obj) for calculo_ch_obj in CalculoCHSemanalAulas.objects.filter(relatorio_id=id)]
        atividade_pedagogica_complementar_dicts = [model_to_dict(atividade_pedagogica_obj) for atividade_pedagogica_obj in AtividadePedagogicaComplementar.objects.filter(relatorio_id=id)]
        atividade_orientacao_supervisao_preceptoria_tutoria_dicts = [model_to_dict(atividade_orientacao_obj) for atividade_orientacao_obj in AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.filter(relatorio_id=id)]
        descricao_orientacao_coorientacao_academica_dicts = [model_to_dict(descricao_orientacao_obj) for descricao_orientacao_obj in DescricaoOrientacaoCoorientacaoAcademica.objects.filter(relatorio_id=id)]
        supervisao_academica_dicts = [model_to_dict(supervisao_academica_obj) for supervisao_academica_obj in SupervisaoAcademica.objects.filter(relatorio_id=id)]
        preceptoria_tutoria_residencia_dicts = [model_to_dict(preceptoria_tutoria_obj) for preceptoria_tutoria_obj in PreceptoriaTutoriaResidencia.objects.filter(relatorio_id=id)]
        banca_examinadora_dicts = [model_to_dict(banca_examinadora_obj) for banca_examinadora_obj in BancaExaminadora.objects.filter(relatorio_id=id)]
        ch_semanal_atividade_ensino_dicts = [model_to_dict(ch_semanal_atividade_obj) for ch_semanal_atividade_obj in CHSemanalAtividadeEnsino.objects.filter(relatorio_id=id)]
        avaliacao_discente_dicts = [model_to_dict(avaliacao_discente_obj) for avaliacao_discente_obj in AvaliacaoDiscente.objects.filter(relatorio_id=id)]
        pesquisa_producao_dict = [model_to_dict(pesquisa_producao_obj) for pesquisa_producao_obj in ProjetoPesquisaProducaoIntelectual.objects.filter(relatorio_id=id)]
        trabalhos_completos_dict = [model_to_dict(trabalhos_completos_obj) for trabalhos_completos_obj in TrabalhoCompletoPublicadoPeriodicoBoletimTecnico.objects.filter(relatorio_id=id)]
        livros_verbetes_publicados_dict = [model_to_dict(livros_verbetes_publicados_obj) for livros_verbetes_publicados_obj in LivroCapituloVerbetePublicado.objects.filter(relatorio_id=id)]
        trabalhos_completos_congressos_dict = [model_to_dict(trabalhos_completos_congressos_obj) for trabalhos_completos_congressos_obj in TrabalhoCompletoResumoPublicadoApresentadoCongressos.objects.filter(relatorio_id=id)]
        outras_atividades_dict = [model_to_dict(outras_atividades_obj) for outras_atividades_obj in OutraAtividadePesquisaProducaoIntelectual.objects.filter(relatorio_id=id)]
        ch_semanal_pesquisa_dict = [model_to_dict(ch_semanal_pesquisa_obj) for ch_semanal_pesquisa_obj in CHSemanalAtividadesPesquisa.objects.filter(relatorio_id=id)]
        projetos_extensao_dict = [model_to_dict(projetos_extensao_obj) for projetos_extensao_obj in ProjetoExtensao.objects.filter(relatorio_id=id)]
        estagios_extensao_dict = [model_to_dict(estagios_extensao_obj) for estagios_extensao_obj in EstagioExtensao.objects.filter(relatorio_id=id)]
        atividade_ensino_naoformal_dict = [model_to_dict(atividade_ensino_naoformal_obj) for atividade_ensino_naoformal_obj in AtividadeEnsinoNaoFormal.objects.filter(relatorio_id=id)]
        outras_atividade_extensao_dict = [model_to_dict(outras_atividade_extensao_obj) for outras_atividade_extensao_obj in OutraAtividadeExtensao.objects.filter(relatorio_id=id)]
        ch_semanal_atividades_extensao_dict = [model_to_dict(ch_semanal_atividades_extensao_obj) for ch_semanal_atividades_extensao_obj in CHSemanalAtividadesExtensao.objects.filter(relatorio_id=id)]
        atividades_gestao_representacao_dict = [model_to_dict(atividades_gestao_representacao_obj) for atividades_gestao_representacao_obj in AtividadeGestaoRepresentacao.objects.filter(relatorio_id=id)]
        qualificacao_docente_dict = [model_to_dict(qualificacao_docente_obj) for qualificacao_docente_obj in QualificacaoDocenteAcademicaProfissional.objects.filter(relatorio_id=id)]
        distribuicao_ch_semanal_dict = [model_to_dict(distribuicao_ch_semanal_obj) for distribuicao_ch_semanal_obj in DistribuicaoCHSemanal.objects.filter(relatorio_id=id)]
        outras_informacoes_dict = [model_to_dict(outras_informacoes_obj) for outras_informacoes_obj in OutraInformacao.objects.filter(relatorio_id=id)]
        afastamentos_dict = [model_to_dict(afastamentos_obj) for afastamentos_obj in Afastamento.objects.filter(relatorio_id=id)]

        merged_data = {}
        merged_data['usuario'] = usuario_dicts
        merged_data['relatorio_docente'] = relatorio_docente_dicts
        merged_data['atividade_letiva'] = atividade_letiva_dicts
        merged_data['calculo_ch_semanal_aulas'] = calculo_ch_semanal_aulas_dicts
        merged_data['atividade_pedagogica_complementar'] = atividade_pedagogica_complementar_dicts
        merged_data['atividade_orientacao_supervisao_preceptoria_tutoria'] = atividade_orientacao_supervisao_preceptoria_tutoria_dicts
        merged_data['descricao_orientacao_coorientacao_academica'] = descricao_orientacao_coorientacao_academica_dicts
        merged_data['supervisao_academica'] = supervisao_academica_dicts
        merged_data['preceptoria_tutoria_residencia'] = preceptoria_tutoria_residencia_dicts
        merged_data['banca_examinadora'] = banca_examinadora_dicts
        merged_data['ch_semanal_atividade_ensino'] = ch_semanal_atividade_ensino_dicts
        merged_data['avaliacao_discente'] = avaliacao_discente_dicts
        merged_data['pesquisa_producao'] = pesquisa_producao_dict
        merged_data['trabalhos_completos'] = trabalhos_completos_dict
        merged_data['livros_verbetes_publicados'] = livros_verbetes_publicados_dict
        merged_data['trabalhos_completos_congressos'] = trabalhos_completos_congressos_dict
        merged_data['outras_atividades'] = outras_atividades_dict
        merged_data['ch_semanal_pesquisa'] = ch_semanal_pesquisa_dict
        merged_data['projetos_extensao'] = projetos_extensao_dict
        merged_data['estagios_extensao'] = estagios_extensao_dict
        merged_data['atividade_ensino_naoformal'] = atividade_ensino_naoformal_dict
        merged_data['outras_atividade_extensao'] = outras_atividade_extensao_dict
        merged_data['ch_semanal_atividades_extensao'] = ch_semanal_atividades_extensao_dict
        merged_data['atividades_gestao_representacao'] = atividades_gestao_representacao_dict
        merged_data['qualificacao_docente'] = qualificacao_docente_dict
        merged_data['distribuicao_ch_semanal'] = distribuicao_ch_semanal_dict
        merged_data['outras_informacoes'] = outras_informacoes_dict
        merged_data['afastamentos'] = afastamentos_dict

        return escrever_dados_no_radoc(merged_data)

    def get(self, request, nome_relatorio=None):
        if nome_relatorio:
            usuario_id = request.user.id
            try:
                instance = RelatorioDocente.objects.get(nome=nome_relatorio, usuario_id=usuario_id)
                Util.calcular_distribuicao_ch_semanal(instance.pk)
                output_pdf = PdfWriter()

                # Aqui será inserida a lógica de preenchimento de RADOC
                binary_radoc = self.gerarPDFRadoc(instance.pk, usuario_id)
                output_pdf.append_pages_from_reader(PdfReader(BytesIO(binary_radoc)))

                documentos_comprobatorios = DocumentoComprobatorio.objects.filter(relatorio_id=instance.pk)
                for documento in documentos_comprobatorios:
                    binary_data = documento.binary_pdf
                    if not self.is_pdf(binary_data):
                        return Util.response_bad_request(f'Erro: O documento comprobatório não é um arquivo PDF válido.')

                    output_pdf.append_pages_from_reader(PdfReader(BytesIO(binary_data)))

                output_buffer = BytesIO()
                output_buffer.truncate(0)
                output_pdf.write(output_buffer)
                output_buffer.seek(0)

                # Retorna o arquivo PDF diretamente como resposta
                response = HttpResponse(output_buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="Relatório Docente - UFRA"'
                return response

            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o nome fornecido')

        return Util.response_bad_request('É necessário fornecer o nome do relatorio_docente que você deseja gerar em download_relatorio/{nome_relatorio}/')
    
class ExtrairDadosAtividadesLetivasPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        arquivo_pdf = request.FILES.get('pdf')
        opcao = request.data.get('opcao')

        if arquivo_pdf:
            try:
                coordinator = PDFExtractionCoordinator()
                dados_extraidos = coordinator.extract_data(arquivo_pdf, opcao)

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

