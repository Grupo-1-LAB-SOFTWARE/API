from django.core.mail import send_mail, EmailMessage, get_connection
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import Usuario, CalculoCHSemanalAulas, AtividadeLetiva, CHSemanalAtividadeEnsino
from django.contrib.auth.models import User
from django.conf import settings
from decouple import config
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

class Util:
    @staticmethod
    def send_verification_email(user_login, user_email, request):
        login = user_login
        print(login)
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'username': user_login})
        activate_url = 'http://'+domain+link

        subject = 'Ative sua conta'
        message = f'Clique no link para verificar sua conta: \n\n {activate_url}'
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
        return Response(chave_token, status=status.HTTP_200_OK)

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
    
    @staticmethod
    def validar_semestre(semestre):
        if semestre > 2 or semestre < 1:
            raise ValidationError({'semestre': ['ERRO: O semestre pode ser apenas 1 ou 2']})
    
    @staticmethod
    def resetar_valores_calculos_ch_semanal_aulas(relatorio_id):
        calculos_ch_semanal_aulas = CalculoCHSemanalAulas.objects.filter(relatorio_id=relatorio_id)
        ch_semanal_atividade_ensino = None

        try:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id=relatorio_id)

        except CHSemanalAtividadeEnsino.DoesNotExist:
            ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                relatorio_id = relatorio_id,
                ch_semanal_primeiro_semestre = 0.0,
                ch_semanal_segundo_semestre = 0.0
            )

            for calculo_ch_semanal_aulas in calculos_ch_semanal_aulas:
                if calculo_ch_semanal_aulas.semestre == 1:
                    ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre - calculo_ch_semanal_aulas.ch_semanal_total
                else:
                    ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre - calculo_ch_semanal_aulas.ch_semanal_total

                ch_semanal_atividade_ensino.save()
                calculo_ch_semanal_aulas.ch_semanal_graduacao = 0.0
                calculo_ch_semanal_aulas.ch_semanal_pos_graduacao = 0.0
                calculo_ch_semanal_aulas.ch_semanal_total = 0.0
                calculo_ch_semanal_aulas.save()

    @staticmethod
    def recriar_calculos_ch_semanal_aulas(relatorio_id):
        atividades_letivas = AtividadeLetiva.objects.filter(relatorio_id=relatorio_id)
        for instance in atividades_letivas:
                ch_usuario = instance.docentes_envolvidos_e_cargas_horarias.pop(relatorio_id.usuario_id.nome_completo.upper(), None)
                try:
                    calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.get(relatorio_id=relatorio_id, semestre=instance.semestre)

                    if instance.nivel == 'GRA':
                        if ch_usuario % 15 == 0:
                            calculo_ch_semanal_aulas.ch_semanal_graduacao = calculo_ch_semanal_aulas.ch_semanal_graduacao + round(ch_usuario / 15, 1)
                                
                        else:
                            calculo_ch_semanal_aulas.ch_semanal_graduacao = calculo_ch_semanal_aulas.ch_semanal_graduacao + round(ch_usuario / 17, 1)

                    elif instance.nivel == 'POS':
                        calculo_ch_semanal_aulas.ch_semanal_pos_graduacao = calculo_ch_semanal_aulas.ch_semanal_pos_graduacao + round(ch_usuario / 15, 1)

                    calculo_ch_semanal_aulas.save()

                except CalculoCHSemanalAulas.DoesNotExist:
                    if instance.nivel == 'GRA':
                        ch_semanal_graduacao = None

                        if ch_usuario % 15 == 0:
                            ch_semanal_graduacao = round(ch_usuario / 15, 1)
                        else:
                            ch_semanal_graduacao = round(ch_usuario / 17, 1)

                        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.create(
                            relatorio_id = relatorio_id,
                            semestre = instance.semestre,
                            ch_semanal_graduacao = ch_semanal_graduacao,
                            ch_semanal_pos_graduacao = 0.0,
                            ch_semanal_total = ch_semanal_graduacao
                        )

                    elif instance.nivel == 'POS':
                        ch_semanal_pos_graduacao = round(ch_usuario / 15, 1)

                        calculo_ch_semanal_aulas = CalculoCHSemanalAulas.objects.create(
                            relatorio_id = relatorio_id,
                            semestre = instance.semestre,
                            ch_semanal_graduacao = 0.0,
                            ch_semanal_pos_graduacao = ch_semanal_pos_graduacao,
                            ch_semanal_total = ch_semanal_pos_graduacao
                        )

    @staticmethod
    def aplicar_maximos_e_minimos_calculos_ch_semanal_aulas(relatorio_id):
        calculos_ch_semanal_aulas = CalculoCHSemanalAulas.objects.filter(relatorio_id=relatorio_id)
        for instance in calculos_ch_semanal_aulas:
            if instance.ch_semanal_graduacao >= 16.0: instance.ch_semanal_graduacao = 16.0
            if instance.ch_semanal_pos_graduacao >= 16.0: instance.ch_semanal_pos_graduacao = 16.0
            if instance.ch_semanal_graduacao < 8.0: instance.ch_semanal_graduacao = 0.0
            if instance.ch_semanal_pos_graduacao < 8.0: instance.ch_semanal_pos_graduacao = 0.0

            instance.ch_semanal_graduacao = round(instance.ch_semanal_graduacao, 1)
            instance.ch_semanal_pos_graduacao = round(instance.ch_semanal_pos_graduacao, 1)

            instance.ch_semanal_total = instance.ch_semanal_graduacao + instance.ch_semanal_pos_graduacao

            instance.save()
            
            ch_semanal_atividade_ensino = None

            try:
                ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.get(relatorio_id=relatorio_id)

            except CHSemanalAtividadeEnsino.DoesNotExist:
                ch_semanal_atividade_ensino = CHSemanalAtividadeEnsino.objects.create(
                    relatorio_id = relatorio_id,
                    ch_semanal_primeiro_semestre = 0.0,
                    ch_semanal_segundo_semestre = 0.0
                )

            if instance.semestre == 1:
                ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre = ch_semanal_atividade_ensino.ch_semanal_primeiro_semestre + instance.ch_semanal_total
            else:
                ch_semanal_atividade_ensino.ch_semanal_segundo_semestre = ch_semanal_atividade_ensino.ch_semanal_segundo_semestre + instance.ch_semanal_total

            ch_semanal_atividade_ensino.save()