from django.core.mail import send_mail, EmailMessage, get_connection
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import Usuario
from django.contrib.auth.models import User
from bson import ObjectId
from django.conf import settings
from decouple import config
from rest_framework.response import Response
from rest_framework import status

class Util:
    @staticmethod
    def send_verification_email(user_login, user_email, request):
        login = user_login
        print(login)
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'username': user_login})
        activate_url = 'http://'+domain+link

        subject = 'Ative sua conta'
        message = f'Clique no link para verificar sua conta \n {activate_url}'
        from_email = from_email = config('EMAIL_HOST_USER')
        recipient_list = [user_email]

        connection = get_connection()

        send_mail(subject, message, from_email, recipient_list, connection=connection)

    @staticmethod
    def response_ok(mensagem_personalizada):
        return Response({"sucess": f"{mensagem_personalizada}"}, status=status.HTTP_200_OK)

    @staticmethod
    def response_ok_no_message(mensagem_personalizada):
        return Response(mensagem_personalizada, status=status.HTTP_200_OK)

    @staticmethod
    def response_ok_token(chave_token):
        return Response({"token": f"{chave_token}"}, status=status.HTTP_200_OK)

    @staticmethod
    def response_created(mensagem_personalizada):
        return Response(mensagem_personalizada, status=status.HTTP_201_CREATED)

    @staticmethod
    def response_bad_request(mensagem_personalizada):
        return Response({"bad_request": f"{mensagem_personalizada}"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def response_not_found(mensagem_personalizada):
        return Response({"not_found": f"{mensagem_personalizada}"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def response_unauthorized(mensagem_personalizada):
        return Response({"unauthorized": f"{mensagem_personalizada}"}, status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def response_forbidden(mensagem_personalizada):
        return Response({"forbidden": f"{mensagem_personalizada}"}, status=status.HTTP_403_FORBIDDEN)
