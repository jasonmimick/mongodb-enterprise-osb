FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

RUN mkdir /mdb-osb-templates
COPY ./app /app

