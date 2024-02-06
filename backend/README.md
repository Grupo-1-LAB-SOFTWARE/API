# Instalar MongoDB
- [Download Compass](https://www.mongodb.com/products/tools/compass)
- [Download MongoDB](https://www.mongodb.com/try/download/community)
- [Tutorial de Instalação no Windowns](https://www.youtube.com/watch?v=rtAPwlvoNoI)

# Configuração do Ambiente

## 1. ativar ambiente virtual (venv)
### certifique-se de estar no diretório /backend

### Windowns
- venv\Scripts\activate

### MacOS Linux
- source venv/bin/activate

## 2. Instalar Dependências do Projeto
- pip install -r requirements.txt

## 3. Executar Migrações do Banco de Dados
- python manage.py migrate

## 4. Executar o Projeto
- python manage.py runserver

### OBS: Criar um arquivo ".env" para as variaveis de ambiente de configuração para envio de email.
Com os seguintes campos:

- EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
- EMAIL_USE_TLS=True
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_HOST_USER= algum_email@gmail.com
- EMAIL_HOST_PASSWORD=[Senha de App Google](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab)
