from django.utils import timezone
from django.urls import get_resolver
from django.forms.models import model_to_dict
from myapp.serializer import (UsuarioSerializer,CampusSerializer,
                              InstitutoSerializer, CursoSerializer, 
                              AtividadeLetivaSerializer, AtividadePedagogicaComplementarSerializer, 
                              AtividadeOrientacaoSerializer, BancaExaminacaoSerializer)
from .models import (Usuario, Campus, 
                     Instituto, Curso, 
                     AtividadeLetiva, AtividadePedagogicaComplementar, 
                     AtividadeOrientacao, BancaExaminacao
                     )
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
                    return Util.response_unauthorized('Não é permitido atualizar o campo "id"')
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
                    return Response({'message': 'Email de verificação enviado'}, status=status.HTTP_201_CREATED)
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

    
class CampusView(APIView):
    def get(self, request, campus_id=None):
        if campus_id:
            return self.getById(request, campus_id)
        else:
            return self.getAll(request)
        
    def getById(self, request, campus_id):
        try:
            campus = Campus.objects.get(pk=campus_id)
            serializer = CampusSerializer(campus)
            return Util.response_ok_no_message(serializer.data)
        except Campus.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar um campus com o id fornecido')

    def getAll(self, request):
        campus = Campus.objects.all()
        serializer = CampusSerializer(campus, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, campus_id):
        if campus_id is not None:
            campus = Campus.objects.get(pk=campus_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualizar o campo "id"')
            serializer = CampusSerializer(campus, data=data, partial=True)
            
    def post(self, request):
        serializer = CampusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors) 

class AtividadeLetivaView(APIView):
    def getAll(self, request):
        atividade_letiva = AtividadeLetiva.objects.all()
        serializer = AtividadeLetivaSerializer(atividade_letiva)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, atividade_letiva_id):
        if atividade_letiva_id is not None:
            atividade_letiva = AtividadeLetiva.objects.get(pk=atividade_letiva_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualiza o campo "id"')
            serializer = AtividadeLetivaSerializer(atividade_letiva, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Util.response_ok_no_message(serializer.data)
            else:
                return Util.response_bad_request(serializer.errors)
                
    def post(self, request):
        serializer = AtividadeLetivaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)
        
class InstitutoView(APIView):
    def get(self, request, instituto_id=None):
        if instituto_id:
            return self.getById(request, instituto_id)
        else:
            return self.getAll(request)
        
    def getById(self, request, instituto_id):
        try:
            instituto = Instituto.objects.get(pk=instituto_id)
            serializer = InstitutoSerializer(instituto)
            return Util.response_ok_no_message(serializer.data)
        except Instituto.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar um instituto com o id fornecido.')
        
    def getAll(self, request):
        instituto = Instituto.objects.all()
        serializer = InstitutoSerializer(instituto, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, instituto_id):
        if instituto_id is not None:
            instituto = Instituto.objects.get(pk=instituto_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualizar o campo "id"')
            serializer = InstitutoSerializer(instituto, data=data, partial=True)
       
    def post(self, request):
        serializer = InstitutoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)         
 
class AtividadePedagogicaComplementarView(APIView):
    def getAll(self, request):
        atividade_pedagogicacomp = AtividadeLetiva.objects.all()
        serializer = AtividadeLetivaSerializer(atividade_pedagogicacomp)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, atividade_pedagogicacomp_id):
        if atividade_pedagogicacomp_id is not None:
            atividade_pedagogicacomp = AtividadePedagogicaComplementar.objects.get(pk=atividade_pedagogicacomp_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualiza o campo "id"')
            serializer = AtividadePedagogicaComplementarSerializer(atividade_pedagogicacomp, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Util.response_ok_no_message(serializer.data)
            else:
                return Util.response_bad_request(serializer.errors)
                
    def post(self, request):
        serializer = AtividadePedagogicaComplementarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)      

class AtividadeOrientaçaoView(APIView):
    def getAll(self, request):
        atividade_orientacao = AtividadeOrientacao.objects.all()
        serializer = AtividadeOrientacaoSerializer(atividade_orientacao)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, atividade_orientacao_id):
        if atividade_orientacao_id is not None:
            atividade_orientacao = AtividadeOrientacao.objects.get(pk=atividade_orientacao_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualiza o campo "id"')
            serializer = AtividadeOrientacaoSerializer(atividade_orientacao, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Util.response_ok_no_message(serializer.data)
            else:
                return Util.response_bad_request(serializer.errors)
                
    def post(self, request):
        serializer = AtividadeOrientacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)
        
  
class CursoView(APIView):
    def get(self, request, curso_id=None):
        if curso_id:
            return self.getById(request, curso_id)
        else:
            return self.getAll(request)
        
    def getById(self, request, curso_id):
        try:
            curso = Curso.objects.get(pk=curso_id)
            serializer = CursoSerializer(curso)
            return Util.response_ok_no_message(serializer.data)
        except Curso.DoesNotExist:
            return Util.response_not_found('Não foi possível encontrar um curso com o id fornecido')
        
    def getAll(self, request):
        curso = Curso.objects.all()
        serializer = CursoSerializer(curso, many=True)
        return Util.response_ok_no_message(serializer.data)
    
    def put(self, request, curso_id):
        if curso_id is not None:
            curso = Curso.objects.get(pk=curso_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualizar o campo "id"')
            serializer = CursoSerializer(curso, data=data, partial=True)
            
    def post(self, request):
        serializer = CursoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)

        
class BancaExaminacaoView(APIView):
    def getAll(self, request):
        banca_examinacao = BancaExaminacao.objects.all()
        serializer = BancaExaminacaoSerializer(banca_examinacao)
        return Util.response_ok_no_message(serializer.data)

    def put(self, request, banca_examinacao_id):
        if banca_examinacao_id is not None:
            banca_examinacao = BancaExaminacao.objects.get(pk=banca_examinacao_id)
            data = request.data.copy()
            if 'id' in data:
                return Util.response_bad_request('Não é possível atualiza o campo "id"')
            serializer = BancaExaminacaoSerializer(banca_examinacao, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Util.response_ok_no_message(serializer.data)
            else:
                return Util.response_bad_request(serializer.errors)
                
    def post(self, request):
        serializer = BancaExaminacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Util.response_ok_no_message(serializer.data)
        else:
            return Util.response_bad_request(serializer.errors)
        
 
class EndpointsView(APIView):
    def get(self, request):
        host = request.get_host()
        urls = get_resolver().reverse_dict.keys()
        return Response({"endpoints": [f"http://{host}/{url}" for url in urls if isinstance(url, str)]})

