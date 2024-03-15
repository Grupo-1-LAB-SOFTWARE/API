from django.utils import timezone
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.serializer import (UsuarioSerializer, RelatorioDocenteSerializer, AtividadeLetivaSerializer, CalculoCHSemanalAulasSerializer, AtividadePedagogicaComplementarSerializer, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer, DescricaoOrientacaoCoorientacaoAcademicaSerializer, SupervisaoAcademicaSerializer, PreceptoriaTutoriaResidenciaSerializer, BancaExaminadoraSerializer, CHSemanalAtividadeEnsinoSerializer, AvaliacaoDiscenteSerializer, ProjetoPesquisaProducaoIntelectualSerializer, TrabalhoCompletoPublicadoPeriodicoBoletimTecnicoSerializer, LivroCapituloVerbetePublicadoSerializer, TrabalhoCompletoResumoPublicadoApresentadoCongressosSerializer, OutraAtividadePesquisaProducaoIntelectualSerializer, CHSemanalAtividadesPesquisaSerializer, ProjetoExtensaoSerializer, EstagioExtensaoSerializer, AtividadeEnsinoNaoFormalSerializer, OutraAtividadeExtensaoSerializer, CHSemanalAtividadesExtensaoSerializer)
from .models import (Usuario, RelatorioDocente, AtividadeLetiva, CalculoCHSemanalAulas, AtividadePedagogicaComplementar, AtividadeOrientacaoSupervisaoPreceptoriaTutoria, DescricaoOrientacaoCoorientacaoAcademica, SupervisaoAcademica, PreceptoriaTutoriaResidencia, BancaExaminadora, CHSemanalAtividadeEnsino, AvaliacaoDiscente, ProjetoPesquisaProducaoIntelectual, TrabalhoCompletoPublicadoPeriodicoBoletimTecnico, LivroCapituloVerbetePublicado, TrabalhoCompletoResumoPublicadoApresentadoCongressos, OutraAtividadePesquisaProducaoIntelectual, CHSemanalAtividadesPesquisa, ProjetoExtensao, EstagioExtensao, AtividadeEnsinoNaoFormal, OutraAtividadeExtensao, CHSemanalAtividadesExtensao)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .services import extrair_texto_do_pdf, extrair_dados_de_atividades_letivas

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
        serializer = CalculoCHSemanalAulasSerializer(data=request.data)
        if serializer.is_valid():
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
        serializer = AtividadePedagogicaComplementarSerializer(data=request.data)
        if serializer.is_valid():
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
        serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(data=request.data)
        if serializer.is_valid():
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
        serializer = CHSemanalAtividadeEnsinoSerializer(data=request.data)
        if serializer.is_valid():
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
        serializer = CHSemanalAtividadesPesquisaSerializer(data=request.data)
        if serializer.is_valid():
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
        serializer = CHSemanalAtividadesExtensaoSerializer(data=request.data)
        if serializer.is_valid():
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

class ExtrairDadosAtividadesLetivasPDFAPIView(APIView):
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

