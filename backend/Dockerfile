FROM python:3.10.12

RUN apt-get update
RUN apt-get -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

WORKDIR /app

RUN pip install pipenv

RUN pip install requeriments.txt

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile

COPY . ./

CMD pipenv run python DepistClic/manage.py migrate && pipenv run python DepistClic/manage.py collectstatic --no-input && pipenv run gunicorn locallibrary.wsgi