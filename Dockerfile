FROM python:3.7-alpine

# Recommended when run python on docker
# It doesnt buffer python on execution, prints directly
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# Install postgres app
RUN apk add --update --no-cache postgresql-client
# Install required apps to install postgres app
# set an alias in order to remove them afterwards
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
# Remove temporary apps
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user, do not use root
RUN adduser -D user
USER user

