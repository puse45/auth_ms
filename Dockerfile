FROM python:3.12

MAINTAINER Pius Musyoki

RUN apt-get update && apt-get install build-essential binutils libproj-dev -y

# Python Domain
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# arbitrary location choice: you can change the directory
RUN mkdir -p /ms_auth
WORKDIR /ms_auth

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# copy our project code
COPY . /ms_auth
RUN chmod a+x /ms_auth/entrypoint.sh
RUN chmod a+x /ms_auth/wait-for-it.sh

# define the default command to run when starting the container
ENTRYPOINT ["/ms_auth/entrypoint.sh"]
