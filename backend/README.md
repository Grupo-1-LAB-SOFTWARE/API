# Instalar MongoDB
- [Download Compass](https://www.mongodb.com/products/tools/compass)
- [Download MongoDB](https://www.mongodb.com/try/download/community)
- [Tutorial de Instalação no Windows](https://www.youtube.com/watch?v=rtAPwlvoNoI)
## Iniciar o servidor do MongoDB e realizar as migrações após a configuração do ambiente.

# Configuração do Ambiente

## 1. ativar ambiente virtual (venv)
### certifique-se de estar no diretório /backend
### considere para MacOS ou Linux utilizar "python3" e "pip3"

### Criar venv:
- python -m venv venv

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

### OBS: Criar um arquivo ".env" dentro da pasta "backend" para as variaveis de ambiente de configuração para envio de email.
Com os seguintes campos:

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

EMAIL_USE_TLS=True

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT=587

EMAIL_HOST_USER= algum_email@gmail.com

EMAIL_HOST_PASSWORD=[Senha de App Google - Clique aqui e siga as instruções em "The Gmail Part"](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab)

### OBS: Caso você esteja usando vs code, após ativar sua venv considere:
#### Windows
- Ctrl + Shift + P
#### MacOs
- Cmmd + Shift + P

- Digitar: Python Select Interpreter
- Enter Interpreter path
- copiar o caminho relativo: backend/venv/bin/python
#### Isso evita que a as bibliotecas não sejam encontradas

## 5. Para desenvolver nessa API, sempre utilize os comandos:

- python manage.py makemigrations myapp || python3 manage.py makemigrations myapp (usar toda vez que mudar algo dentro do arquivo myapp/models.py. Esse comando serve para criar uma pasta migrations dentro de myapp que informa como as tabelas devem ser criadas no banco de dados a partir dos models);

- python manage.py migrate || python3 manage.py migrate (usar logo após usar o comando makemigrations. O migrate serve para criar todas as tabelas necessárias no seu banco de dados local. Após utilizar, olhe o seu Database sisradoc e veja que as tabelas foram criadas automaticamente pelo Django);

- python manage.py runserver || python3 manage.py runserver (quando quiser rodar a API localmente).
