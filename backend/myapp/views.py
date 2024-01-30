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

class UsuarioView(APIView):
    def get(self, request, user_id=None):
        if user_id is not None:
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
                raise Http404

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
            raise Http404
    
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_dict = model_to_dict(user)
            user_login = user_dict.get('login', None)
            user_email = user_dict.get('email', None)
            print(user_login)
            print(user_email)
            if (user_login, user_email) is not None:
                Util.send_verification_email(user_login, user_email, request)
                return Response({'message': 'Email de verificação enviado'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        