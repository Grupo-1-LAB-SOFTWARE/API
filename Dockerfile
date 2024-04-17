FROM python:3.10.12

# Instale as dependências necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    postgresql \
    gcc

RUN apt-get -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# Crie e ative o ambiente virtual
RUN python -m venv --copies /opt/venv && . /opt/venv/bin/activate

# Copie os arquivos de requisitos e instale-os
COPY /backend/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# COPY Pipfile Pipfile.lock ./

# RUN pipenv install --deploy --ignore-pipfile

# COPY . ./

# Defina o diretório de trabalho da aplicação
WORKDIR /app

# Copie o restante dos arquivos da aplicação para o contêiner
COPY . /app


CMD python manage.py migrate && gunicorn api_sisradoc.wsgi
# Execute as migrações do Django e inicie o servidor Gunicorn
#CMD pipenv run python DepistClic/manage.py migrate && pipenv run python DepistClic/manage.py collectstatic --no-input && pipenv run gunicorn locallibrary.wsgi



#CMD pipenv run python DepistClic/manage.py migrate && pipenv run python DepistClic/manage.py collectstatic --no-input 
