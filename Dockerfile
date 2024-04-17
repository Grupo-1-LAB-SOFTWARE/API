FROM python:3.10.12

# Instale as dependências necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    postgresql \
    gcc

RUN apt-get -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

RUN python -m venv --copies /opt/venv && . /opt/venv/bin/activate

COPY /backend/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY . /app

CMD python ./backend/manage.py migrate
