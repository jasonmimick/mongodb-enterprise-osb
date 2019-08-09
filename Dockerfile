FROM python:3.7-alpine as base-env
RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

FROM base-env as osb-container
RUN mkdir /mdb-osb-templates
RUN mkdir /etc/mongodb-entperise-osb
COPY ./app /app

WORKDIR /app
CMD [ "python3", "main.py" ]
