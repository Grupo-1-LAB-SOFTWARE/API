from django.core.mail import send_mail, EmailMessage, get_connection
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import Usuario
from django.contrib.auth.models import User
from bson import ObjectId

class Util:
    @staticmethod
    def send_verification_email(user_login, user_email, request):
        login = user_login
        print(login)
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'login': user_login})
        activate_url = 'http://'+domain+link

        subject = 'Ative sua conta'
        message = f'Clique no link para verificar sua conta \n {activate_url}'
        from_email = 'reynanvt@gmail.com'
        recipient_list = [user_email]

        connection = get_connection()

        send_mail(subject, message, from_email, recipient_list, connection=connection)
