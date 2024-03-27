from django.utils import timezone
import tempfile
import os
import fitz 
from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.extraction_strategy import PDFExtractionCoordinator
from myapp.serializer import (UsuarioSerializer, RelatorioDocenteSerializer, AtividadeLetivaSerializer, CalculoCHSemanalAulasSerializer, AtividadePedagogicaComplementarSerializer, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer, DescricaoOrientacaoCoorientacaoAcademicaSerializer, SupervisaoAcademicaSerializer, PreceptoriaTutoriaResidenciaSerializer, BancaExaminadoraSerializer, CHSemanalAtividadeEnsinoSerializer, AvaliacaoDiscenteSerializer, ProjetoPesquisaProducaoIntelectualSerializer, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer, LivroCapituloVerbetePublicadoSerializer, TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer, OutraAtividadePesquisaProducaoIntelectualSerializer, CHSemanalAtividadesPesquisaSerializer, ProjetoExtensaoSerializer, EstagioExtensaoSerializer, AtividadeEnsinoNaoFormalSerializer, OutraAtividadeExtensaoSerializer, CHSemanalAtividadesExtensaoSerializer, DistribuicaoCHSemanalSerializer, AtividadeGestaoRepresentacaoSerializer, QualificacaoDocenteAcademicaProfissionalSerializer, OutraInformacaoSerializer, AfastamentoSerializer, DocumentoComprobatorioSerializer)
from .models import (Usuario, RelatorioDocente, AtividadeLetiva, CalculoCHSemanalAulas, AtividadePedagogicaComplementar, AtividadeOrientacaoSupervisaoPreceptoriaTutoria, DescricaoOrientacaoCoorientacaoAcademica, SupervisaoAcademica, PreceptoriaTutoriaResidencia, BancaExaminadora, CHSemanalAtividadeEnsino, AvaliacaoDiscente, ProjetoPesquisaProducaoIntelectual, TrabalhoCompletoPublicadoPeriodicoBoletimTecnico, LivroCapituloVerbetePublicado, TrabalhoCompletoResumoPublicadoApresentadoCongressos, OutraAtividadePesquisaProducaoIntelectual, CHSemanalAtividadesPesquisa, ProjetoExtensao, EstagioExtensao, AtividadeEnsinoNaoFormal, OutraAtividadeExtensao, CHSemanalAtividadesExtensao, DistribuicaoCHSemanal, AtividadeGestaoRepresentacao, QualificacaoDocenteAcademicaProfissional, OutraInformacao, Afastamento, DocumentoComprobatorio)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .services import escrever_dados_no_pdf, extrair_texto_do_pdf, extrair_dados_de_atividades_letivas

class UsuarioView(APIView):
    def get(self, request, user_id=None):
        if user_id:
            return self.getById(request, user_id)
        else:
            return self.getAll(request)
            
    def put(self, request, user_id=None):
        if user_id is not None:
            try:
                user = Usuario.objects.get(pk=user_id)
                data = request.data.copy()
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')
                if 'is_active' in data:
                    return Util.response_unauthorized('Não é permitido atualizar o campo "is_active"')
                if 'date_joined' in data:
                    return Util.response_unauthorized('Não é permitido atualizar o campo "date_joined"')

                username = request.data.get('username')
                email = request.data.get('email')
                if self.is_username_disponivel(username) == False:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
                if self.is_email_disponivel(email) == False:
                    return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')

                serializer = UsuarioSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do usuário que você deseja atualizar em usuarios/{id}')


    #Pra pegar todos os usuários, sem especificar id
    def getAll(self, request):
        user = Usuario.objects.all()
        serializer = UsuarioSerializer(user, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, user_id=None):
        if user_id:
            try:
                user = Usuario.objects.get(pk=user_id)
                serializer = UsuarioSerializer(user)
                return Util.response_ok_no_message(serializer.data)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em usuarios/{id}/')
    
    def post(self, request):
            username = request.data.get('username')
            email = request.data.get('email')
            
            if self.is_username_disponivel(username) == False:
                return Util.response_bad_request('Já existe um usuário cadastrado com esse username.')
            if self.is_email_disponivel(email) == False:
                return Util.response_bad_request('Já existe um usuário cadastrado com esse e-mail.')

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
        
    def delete(self, request, user_id=None):
        if user_id:
            try:
                instance = Usuario.objects.get(pk=user_id)
                instance.delete()
                return Util.response_ok_no_message('Usuário excluído com sucesso.')
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em usuarios/{id}/')

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
                token, created = Token.objects.get_or_create(user=usuario)
                return Util.response_ok_token(token.key)
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
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)
        
    def post(self, request):
        serializer = AtividadeLetivaSerializer(data=request.data)
        if serializer.is_valid():
            atividade_letiva = serializer.save()
            return Util.response_created(f'id: {atividade_letiva.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                atividade_letiva = AtividadeLetiva.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AtividadeLetivaSerializer(atividade_letiva, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeLetiva.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da atividade letiva que você deseja atualizar em atividade_letiva/{id}/')

    def getAll(self, request):
        atividades_letivas = AtividadeLetiva.objects.all()
        serializer = AtividadeLetivaSerializer(atividades_letivas, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = AtividadeLetiva.objects.get(pk=id)
                serializer = AtividadeLetivaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AtividadeLetiva.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em atividade_letiva/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AtividadeLetiva.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AtividadeLetiva.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_letiva com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em atividade_letiva/{id}/')

class CalculoCHSemanalAulasView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        calculo_ch_semanal_aulas = None
        serializer = CalculoCHSemanalAulasSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = CalculoCHSemanalAulas.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 2:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionados dois calculo_ch_semanal_aulas para cada relatorio_docente. Um para cada semestre.')
                    if instances[0].semestre is 1 and serializer.validated_data.get('semestre') is 1:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionado um calculo_ch_semanal_aulas por semestre para cada relatorio_docente.')
                    if instances[0].semestre is 2 and serializer.validated_data.get('semestre') is 2:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionado um calculo_ch_semanal_aulas por semestre para cada relatorio_docente.')
                
                calculo_ch_semanal_aulas = serializer.save()

            except CalculoCHSemanalAulas.DoesNotExist:
                calculo_ch_semanal_aulas = serializer.save()
            return Util.response_created(f'id: {calculo_ch_semanal_aulas.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = CalculoCHSemanalAulasSerializer(calculo_ch_semanal_aulas, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except CalculoCHSemanalAulas.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um calculo_ch_semanal_aulas com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da calculo_ch_semanal_aulas que você deseja atualizar em calculo_ch_semanal_aulas/{id}/')


    def getAll(self, request):
        calculos_ch_semanal_aulas = CalculoCHSemanalAulas.objects.all()
        serializer = CalculoCHSemanalAulasSerializer(calculos_ch_semanal_aulas, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, id=None):
        if id:
            try:
                instance = CalculoCHSemanalAulas.objects.get(pk=id)
                serializer = CalculoCHSemanalAulasSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except CalculoCHSemanalAulas.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um calculo_ch_semanal_aulas com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em calculo_ch_semanal_aulas/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = CalculoCHSemanalAulas.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except CalculoCHSemanalAulas.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um calculo_ch_semanal_aulas com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em calculo_ch_semanal_aulas/{id}/')


class AtividadePedagogicaComplementarView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        atividade_pedagogica_complementar = None
        serializer = AtividadePedagogicaComplementarSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = AtividadePedagogicaComplementar.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 2:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas atividade_pedagogica_complementar para cada relatorio_docente. Uma para cada semestre.')
                    if instances[0].semestre is 1 and serializer.validated_data.get('semestre') is 1:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')
                    if instances[0].semestre is 2 and serializer.validated_data.get('semestre') is 2:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_pedagogica_complementar por semestre para cada relatorio_docente.')
                
                atividade_pedagogica_complementar = serializer.save()

            except AtividadePedagogicaComplementar.DoesNotExist:
                atividade_pedagogica_complementar = serializer.save()

            return Util.response_created(f'id: {atividade_pedagogica_complementar.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                ativiade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AtividadePedagogicaComplementarSerializer(ativiade_pedagogica_complementar, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadePedagogicaComplementar.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja atualizar em atividade_pedagogica_complementar/{id}/')

    def getAll(self, request):
        atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.all()
        serializer = AtividadePedagogicaComplementarSerializer(atividade_pedagogica_complementar, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, id=None):
        if id:
            try:
                instance = AtividadePedagogicaComplementar.objects.get(pk=id)
                serializer = AtividadePedagogicaComplementarSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AtividadePedagogicaComplementar.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em atividade_pedagogica_complementar/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AtividadePedagogicaComplementar.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AtividadePedagogicaComplementar.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em atividade_pedagogica_complementar/{id}/')

class AtividadeOrientacaoSupervisaoPreceptoriaTutoriaView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        instance = None
        serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 2:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionadas duas atividade_orientacao_supervisao_preceptoria_tutoria para cada relatorio_docente. Uma para cada semestre.')
                    if instances[0].semestre is 1 and serializer.validated_data.get('semestre') is 1:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')
                    if instances[0].semestre is 2 and serializer.validated_data.get('semestre') is 2:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma atividade_orientacao_supervisao_preceptoria_tutoria por semestre para cada relatorio_docente.')
                
                instance = serializer.save()

            except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                instance = serializer.save()

            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em atividade_orientacao_supervisao_preceptoria_tutoria/{id}/')

    def getAll(self, request):
        instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.all()
        serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id)
                serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em atividade_orientacao_supervisao_preceptoria_tutoria/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em atividade_orientacao_supervisao_preceptoria_tutoria/{id}/')

class DescricaoOrientacaoCoorientacaoAcademicaView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em descricao_orientacao_coorientacao_academica/{id}/')

    def getAll(self, request):
        instances = DescricaoOrientacaoCoorientacaoAcademica.objects.all()
        serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id)
                serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em descricao_orientacao_coorientacao_academica/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em descricao_orientacao_coorientacao_academica/{id}/')
    
class SupervisaoAcademicaView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = SupervisaoAcademicaSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = SupervisaoAcademica.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = SupervisaoAcademicaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except SupervisaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em supervisao_academica/{id}/')

    def getAll(self, request):
        instances = SupervisaoAcademica.objects.all()
        serializer = SupervisaoAcademicaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = SupervisaoAcademica.objects.get(pk=id)
                serializer = SupervisaoAcademicaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except SupervisaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em supervisao_academica/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = SupervisaoAcademica.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except SupervisaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em supervisao_academica/{id}/')

class PreceptoriaTutoriaResidenciaView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = PreceptoriaTutoriaResidenciaSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = PreceptoriaTutoriaResidencia.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = PreceptoriaTutoriaResidenciaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except PreceptoriaTutoriaResidencia.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em preceptoria_tutoria_residencia/{id}/')

    def getAll(self, request):
        instances = PreceptoriaTutoriaResidencia.objects.all()
        serializer = PreceptoriaTutoriaResidenciaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = PreceptoriaTutoriaResidencia.objects.get(pk=id)
                serializer = PreceptoriaTutoriaResidenciaSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except PreceptoriaTutoriaResidencia.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em preceptoria_tutoria_residencia/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = PreceptoriaTutoriaResidencia.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except PreceptoriaTutoriaResidencia.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em preceptoria_tutoria_residencia/{id}/')

class BancaExaminadoraView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = BancaExaminadoraSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = BancaExaminadora.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = BancaExaminadoraSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except BancaExaminadora.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em banca_examinadora/{id}/')

    def getAll(self, request):
        instances = BancaExaminadora.objects.all()
        serializer = BancaExaminadoraSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = BancaExaminadora.objects.get(pk=id)
                serializer = BancaExaminadoraSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except BancaExaminadora.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em banca_examinadora/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = BancaExaminadora.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except BancaExaminadora.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em banca_examinadora/{id}/')

class CHSemanalAtividadeEnsinoView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        instance = None
        serializer = CHSemanalAtividadeEnsinoSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_id = serializer.validated_data.get('relatorio_id')
            try:
                instances = CHSemanalAtividadeEnsino.objects.filter(relatorio_id=relatorio_id)
                if instances.count() > 0:
                    if instances.count() == 1:
                        return Util.response_bad_request('Objeto não criado: só podem ser adicionada uma ch_semanal_atividade_ensino para cada relatorio_docente.')
                
                instance = serializer.save()

            except CHSemanalAtividadeEnsino.DoesNotExist:
                instance = serializer.save()
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = CHSemanalAtividadeEnsino.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = CHSemanalAtividadeEnsinoSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except CHSemanalAtividadeEnsino.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividade_ensino com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em ch_semanal_atividade_ensino/{id}/')

    def getAll(self, request):
        instances = CHSemanalAtividadeEnsino.objects.all()
        serializer = CHSemanalAtividadeEnsinoSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadeEnsino.objects.get(pk=id)
                serializer = CHSemanalAtividadeEnsinoSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except CHSemanalAtividadeEnsino.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividade_ensino com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em ch_semanal_atividade_ensino/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = CHSemanalAtividadeEnsino.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except CHSemanalAtividadeEnsino.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ch_semanal_atividade_ensino com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em ch_semanal_atividade_ensino/{id}/')

class AvaliacaoDiscenteView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = AvaliacaoDiscenteSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = AvaliacaoDiscente.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = AvaliacaoDiscenteSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AvaliacaoDiscente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em avaliacao_discente/{id}/')

    def getAll(self, request):
        instances = AvaliacaoDiscente.objects.all()
        serializer = AvaliacaoDiscenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = AvaliacaoDiscente.objects.get(pk=id)
                serializer = AvaliacaoDiscenteSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except AvaliacaoDiscente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em avaliacao_discente/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = AvaliacaoDiscente.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except AvaliacaoDiscente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma avaliacao_discente com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em avaliacao_discente/{id}/')

class ProjetoPesquisaProducaoIntelectualView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = ProjetoPesquisaProducaoIntelectualSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = ProjetoPesquisaProducaoIntelectual.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data or 'relatorio_id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id ou relatorio_id')

                serializer = ProjetoPesquisaProducaoIntelectualSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma projeto_pesquisa_producao_intelectual com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em projeto_pesquisa_producao_intelectual/{id}/')

    def getAll(self, request):
        instances = ProjetoPesquisaProducaoIntelectual.objects.all()
        serializer = ProjetoPesquisaProducaoIntelectualSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
        
    def getById(self, request, id=None):
        if id:
            try:
                instance = ProjetoPesquisaProducaoIntelectual.objects.get(pk=id)
                serializer = ProjetoPesquisaProducaoIntelectualSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um projeto_pesquisa_producao_intelectual com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em projeto_pesquisa_producao_intelectual/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = ProjetoPesquisaProducaoIntelectual.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('Objeto excluído com sucesso.')
            except ProjetoPesquisaProducaoIntelectual.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um projeto_pesquisa_producao_intelectual com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em projeto_pesquisa_producao_intelectual/{id}/')


class TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoView(APIView):
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
                    if instances[0].semestre is 1 and serializer.validated_data.get('semestre') is 1:
                        return Util.response_bad_request('Objeto não criado: só pode ser adicionada uma distribuicao_ch_semanal por semestre para cada relatorio_docente.')
                    if instances[0].semestre is 2 and serializer.validated_data.get('semestre') is 2:
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
    def post(self, request):
        serializer = RelatorioDocenteSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_docente = serializer.save()
            return Util.response_created({'id': f'{relatorio_docente.pk}'})
        return Util.response_bad_request(serializer.errors)

    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)
        
    def getAll(self, request):
        instances = RelatorioDocente.objects.all()
        serializer = RelatorioDocenteSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def getById(self, request, id=None):
        if id:
            try:
                instance = RelatorioDocente.objects.get(pk=id)
                serializer = RelatorioDocenteSerializer(instance)
                return Util.response_ok_no_message(serializer.data)
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um relatorio_docente com o id fornecido')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja ler em relatorio_docente/{id}/')
        
    def delete(self, request, id=None):
        if id:
            try:
                instance = RelatorioDocente.objects.get(pk=id)
                instance.delete()
                return Util.response_ok_no_message('RADOC excluído com sucesso.')
            except RelatorioDocente.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma relatorio_docente com o id fornecido.')
        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja excluir em relatorio_docente/{id}/')
    
class DownloadRelatorioDocenteView(APIView):
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

class GerarRelatorioDocenteView(APIView):
    def get(self, request, relatorio_id, usuario_id):
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

        return Response({escrever_dados_no_pdf(merged_data)})
 
class EndpointsView(APIView):
    def get(self, request):
        host = request.get_host()
        urls = get_resolver().reverse_dict.keys()
        return Response({"endpoints": [f"http://{host}/{url}" for url in urls if isinstance(url, str)]})

