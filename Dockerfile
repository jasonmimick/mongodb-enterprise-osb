FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN mkdir /mdb-osb-templates

COPY ./app /app
