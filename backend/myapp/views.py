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
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate

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
                    return Util.response_bad_request('Não é possível atualizar o campo "id"')
                if 'is_email_confirmado' in data:
                    return Util.response_bad_request('Não é possível atualizar o campo "is_email_confirmado"')

                serializer = UsuarioSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return Util.response_ok_no_message(serializer.data)
                else:
                    return Util.response_bad_request(serializer.errors)

            except Usuario.DoesNotExist:
                return Util.response_not_found('Não foi possível encontrar um usuário com o id fornecido')


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
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_dict = model_to_dict(user)
            user_login = user_dict.get('login', None)
            user_email = user_dict.get('email', None)
            if (user_login, user_email) is not None:
                Util.send_verification_email(user_login, user_email, request)
                return Util.response_created(serializer.data)
        return Util.response_bad_request(serializer.errors)


class LoginView(APIView):
    def post(self, request):
        login = request.data.get('login', None)
        email = request.data.get('email', None)
        senha = request.data.get('senha', None)
        if email and senha:
            return self.getToken(None, email, senha)
        if login and senha:
            return self.getToken(login, None, senha)
        return Util.response_unauthorized('É necessário fornecer email e senha ou login e senha para logar')

    def getToken(self, login, email, senha):
        usuario = None
        if email and senha:
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
               return Util.response_not_found('Não existe nenhum usuário cadastrado com esse e-mail.')
        elif login and senha:
            try:
                usuario = Usuario.objects.get(login=login)
            except Usuario.DoesNotExist:
                return Util.response_not_found('Não existe nenhum usuário cadastrado com esse login.')

        if usuario:
            if usuario.is_email_confirmado == False:
                return Util.response_unauthorized('O usuário fornecido não pode realizar login pois ainda não confirmou o seu e-mail.')

            if check_password(senha, usuario.senha):
                token, created = Token.objects.get_or_create(user=usuario)
                return Util.response_ok_token(token.key)
            else:
                return Util.response_unauthorized('Senha incorreta.')
        else:
            return Util.response_not_found('Ocorreu algum erro desconhecido')


class ActivateEmail(APIView):
    def get(self, request, login):
        try:
            print(login)
            Usuario.objects.filter(login=login).update(
                is_email_confirmado=True
            )
        except Usuario.DoesNotExist:
            return Util.response_not_found('Usuário não encontrado')

        return Util.response_ok('Ativação do usuário bem-sucedida')
        