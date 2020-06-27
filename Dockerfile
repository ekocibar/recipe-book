FROM python:3.7-alpine

# Recommended when run python on docker
# It doesnt buffer python on execution, prints directly
ENV PYTHONUNBUFFERED 1  

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user, do not use root
RUN adduser -D user
USER user

