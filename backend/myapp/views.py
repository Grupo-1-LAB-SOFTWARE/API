from django.utils import timezone
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.serializer import (UsuarioSerializer, RelatorioDocenteSerializer, AtividadeLetivaSerializer, CalculoCHSemanalAulasSerializer, AtividadePedagogicaComplementarSerializer, AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer, DescricaoOrientacaoCoorientacaoAcademicaSerializer, SupervisaoAcademicaSerializer, PreceptoriaTutoriaResidenciaSerializer, BancasExaminadorasSerializer)
from .models import (Usuario, RelatorioDocente, AtividadeLetiva, CalculoCHSemanalAulas, AtividadePedagogicaComplementar, AtividadeOrientacaoSupervisaoPreceptoriaTutoria, DescricaoOrientacaoCoorientacaoAcademica, SupervisaoAcademica, PreceptoriaTutoriaResidencia, BancasExaminadoras)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password

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
    
    def getById(self, request, user_id):
        try:
            user = Usuario.objects.get(pk=user_id)
            serializer = UsuarioSerializer(user)
            return Util.response_ok_no_message(serializer.data)
        except Usuario.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar um usuário com o id fornecido')
    
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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = AtividadeLetivaSerializer(atividade_letiva, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeLetiva.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma ativiade letiva com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da atividade letiva que você deseja atualizar em atividade_letiva/{id}')


    def getAllAll(self, request):
        atividades_letivas = AtividadeLetiva.objects.all()
        serializer = AtividadeLetivaSerializer(atividades_letivas, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            atividade_letiva = AtividadeLetiva.objects.get(pk=id)
            serializer = AtividadeLetivaSerializer(atividade_letiva)
            return Util.response_ok_no_message(serializer.data)
        except Usuario.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma atividade letiva com o id fornecido')


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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = CalculoCHSemanalAulasSerializer(calculo_ch_semanal_aulas, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except CalculoCHSemanalAulas.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma calculo_ch_semanal_aulas com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da calculo_ch_semanal_aulas que você deseja atualizar em calculo_ch_semanal_aulas/{id}')


    def getAll(self, request):
        calculos_ch_semanal_aulas = CalculoCHSemanalAulas.objects.all()
        serializer = CalculoCHSemanalAulasSerializer(calculos_ch_semanal_aulas, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(pk=id)
            serializer = CalculoCHSemanalAulasSerializer(calculo_ch_semanal_aulas)
            return Util.response_ok_no_message(serializer.data)
        except CalculoCHSemanalAulas.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma calculo_ch_semanal_aulas com o id fornecido')


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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = AtividadePedagogicaComplementarSerializer(ativiade_pedagogica_complementar, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadePedagogicaComplementar.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id da atividade_pedagogica_complementar que você deseja atualizar em atividade_pedagogica_complementar/{id}')

    def getAll(self, request):
        atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.all()
        serializer = AtividadePedagogicaComplementarSerializer(atividade_pedagogica_complementar, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            atividade_pedagogica_complementar = AtividadePedagogicaComplementar.objects.get(pk=id)
            serializer = AtividadePedagogicaComplementarSerializer(atividade_pedagogica_complementar)
            return Util.response_ok_no_message(serializer.data)
        except AtividadePedagogicaComplementar.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma atividade_pedagogica_complementar com o id fornecido')


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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em atividade_orientacao_supervisao_preceptoria_tutoria/{id}')

    def getAll(self, request):
        instances = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.all()
        serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            instance = AtividadeOrientacaoSupervisaoPreceptoriaTutoria.objects.get(pk=id)
            serializer = AtividadeOrientacaoSupervisaoPreceptoriaTutoriaSerializer(instance)
            return Util.response_ok_no_message(serializer.data)
        except AtividadeOrientacaoSupervisaoPreceptoriaTutoria.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma atividade_orientacao_supervisao_preceptoria_tutoria com o id fornecido')

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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em descricao_orientacao_coorientacao_academica/{id}')

    def getAll(self, request):
        instances = DescricaoOrientacaoCoorientacaoAcademica.objects.all()
        serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            instance = DescricaoOrientacaoCoorientacaoAcademica.objects.get(pk=id)
            serializer = DescricaoOrientacaoCoorientacaoAcademicaSerializer(instance)
            return Util.response_ok_no_message(serializer.data)
        except DescricaoOrientacaoCoorientacaoAcademica.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma descricao_orientacao_coorientacao_academica com o id fornecido')
    
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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = SupervisaoAcademicaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except SupervisaoAcademica.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em supervisao_academica/{id}')

    def getAll(self, request):
        instances = SupervisaoAcademica.objects.all()
        serializer = SupervisaoAcademicaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            instance = SupervisaoAcademica.objects.get(pk=id)
            serializer = SupervisaoAcademicaSerializer(instance)
            return Util.response_ok_no_message(serializer.data)
        except SupervisaoAcademica.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma supervisao_academica com o id fornecido')

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
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = PreceptoriaTutoriaResidenciaSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except PreceptoriaTutoriaResidencia.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em preceptoria_tutoria_residencia/{id}')


    def getAll(self, request):
        instances = PreceptoriaTutoriaResidencia.objects.all()
        serializer = PreceptoriaTutoriaResidenciaSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            instance = PreceptoriaTutoriaResidencia.objects.get(pk=id)
            serializer = PreceptoriaTutoriaResidenciaSerializer(instance)
            return Util.response_ok_no_message(serializer.data)
        except PreceptoriaTutoriaResidencia.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma preceptoria_tutoria_residencia com o id fornecido')

class BancasExaminadorasView(APIView):
    def get(self, request, id=None):
        if id:
            return self.getById(request, id)
        else:
            return self.getAll(request)

    def post(self, request):
        serializer = BancasExaminadorasSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save() 
            return Util.response_created(f'id: {instance.pk}')
        return Util.response_bad_request(serializer.errors)

    def put(self, request, id=None):
        if id is not None:
            try:
                instance = BancasExaminadoras.objects.get(pk=id)
                data = request.data.copy()
                if 'id' in data:
                    return Util.response_unauthorized('Não é permitido atualizar nenhum id')

                serializer = BancasExaminadorasSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except BancasExaminadoras.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido.')

        return Util.response_bad_request('É necessário fornecer o id do objeto que você deseja atualizar em banca_examinadora/{id}')

    def getAll(self, request):
        instances = BancasExaminadoras.objects.all()
        serializer = BancasExaminadorasSerializer(instances, many=True)
        return Util.response_ok_no_message(serializer.data)

    def getById(self, request, id):
        try:
            instance = BancasExaminadoras.objects.get(pk=id)
            serializer = BancasExaminadorasSerializer(instance)
            return Util.response_ok_no_message(serializer.data)
        except BancasExaminadoras.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar uma banca_examinadora com o id fornecido')


class RelatorioDocenteView(APIView):

    def post(self, request):
        serializer = RelatorioDocenteSerializer(data=request.data)
        if serializer.is_valid():
            relatorio_docente = serializer.save()
            return Util.response_created({'id': f'{relatorio_docente.pk}'})
        return Util.response_bad_request(serializer.errors)

    def get(self, request):
        radocs = RelatorioDocente.objects.all()
        serializer = RelatorioDocenteSerializer(radocs, many=True)
        return Util.response_ok_no_message(serializer.data)


class EndpointsView(APIView):
    def get(self, request):
        host = request.get_host()
        urls = get_resolver().reverse_dict.keys()
        return Response({"endpoints": [f"http://{host}/{url}" for url in urls if isinstance(url, str)]})

