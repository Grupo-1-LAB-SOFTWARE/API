from django.core.mail import send_mail
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


class UsuarioView(APIView):
    #Pra pegar todos os usuários, sem especificar id
    def get(self, request):
        user = Usuario.objects.all()
        serializer = UsuarioSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # commit=False - Cria o usuário mas não salva
            token = default_token_generator.make_token(user)
            mail_subject = 'Ative sua conta.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
            })
            send_mail(mail_subject, message, 'meu_email@example.com', [user.Email])
            return Response("Por favor confirme seu email para completar o registro.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AtivarContaView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.isEmailConfirmado = True
                user.save()  # Salva o usuário
                return Response("Obrigado pela sua confirmação de email. Agora você pode fazer login na sua conta.")
            else:
                return Response("O link de ativação é inválido!")
        except(TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None
            return Response("O link de ativação é inválido!")
        