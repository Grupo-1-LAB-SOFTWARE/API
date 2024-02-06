from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.contrib.sites.shortcuts import get_current_site
from myapp.serializer import UsuarioSerializer
from myapp.models import Usuario
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from .utils import Util
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password

class UsuarioView(APIView):
    def get(self, request, user_id=None):
        if user_id:
            return self.getById(request, user_id)
        else:
            return self.getAll(request)
            
    def put(self, request, user_id):
        if user_id is not None:
            try:
                user = Usuario.objects.get(pk=user_id)
                data = request.data.copy()
                if 'id' in data:
                    return Response({'error': 'Não é possível atualizar o campo "id"'}, status=status.HTTP_400_BAD_REQUEST)
                if 'is_email_confirmado' in data:
                    return Response({'error': 'Não é possível atualizar o campo "is_email_confirmado"'}, status=status.HTTP_400_BAD_REQUEST)

                serializer = UsuarioSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Usuario.DoesNotExist:
                return Response('{erro: Não foi possível encontrar um usuário com o id fornecido}', status=status.HTTP_404_NOT_FOUND)


    #Pra pegar todos os usuários, sem especificar id
    def getAll(self, request):
        user = Usuario.objects.all()
        serializer = UsuarioSerializer(user, many=True)
        return Response(serializer.data)
    
    def getById(self, request, user_id):
        try:
            user = Usuario.objects.get(pk=user_id)
            serializer = UsuarioSerializer(user)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response('{erro: Não foi possível encontrar um usuário com o id fornecido}', status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_dict = model_to_dict(user)
            user_login = user_dict.get('login', None)
            user_email = user_dict.get('email', None)
            if (user_login, user_email) is not None:
                Util.send_verification_email(user_login, user_email, request)
                return Response({'message': 'Email de verificação enviado'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        login = request.data.get('login', None)
        email = request.data.get('email', None)
        senha = request.data.get('senha', None)
        if email and senha:
            return self.getToken(request, None, email, senha)
        if login and senha:
            return self.getToken(request, login, None, senha)
        return Response({'erro': 'É necessário fornecer email e senha ou login e senha para logar'}, status=status.HTTP_404_NOT_FOUND)

    def getToken(self, request, login, email, senha):
        usuario = None
        if email and senha:
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return Response({'usuario_nao_encontrado': 'Não existe nenhum usuário cadastrado com esse e-mail.'}, status=status.HTTP_404_NOT_FOUND)
        elif login and senha:
            try:
                usuario = Usuario.objects.get(login=login)
            except Usuario.DoesNotExist:
                return Response({'usuario_nao_encontrado': 'Não existe nenhum usuário cadastrado com esse login.'}, status=status.HTTP_404_NOT_FOUND)
        if usuario:
            if check_password(senha, usuario.senha):
                        userUtil = Util.from_usuario_to_user(usuario)
                        token, created = Token.objects.get_or_create(user=userUtil)
                        return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'acesso_negado': 'Senha incorreta.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'erro': 'Ocorreu algum erro desconhecido'}, status=status.HTTP_404_NOT_FOUND)


class ActivateEmail(APIView):
    def get(self, request, login):
        try:
            print(login)
            Usuario.objects.filter(login=login).update(
                is_email_confirmado=True
            )
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Ativação bem-sucedida'}, status=status.HTTP_200_OK)
        