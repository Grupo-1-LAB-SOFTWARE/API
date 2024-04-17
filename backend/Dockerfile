FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

ADD . /app/

EXPOSE 8000

CMD python ./backend/manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#CMD python ./backend/manage.py migrate && python ./backend/manage.py runserver
