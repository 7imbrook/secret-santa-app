FROM python:3.7

WORKDIR /root/santa

# install py deps
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Move source
COPY ./src ./src
COPY ./frontend ./frontend

# Min Env Setup
ENV PROD=true
ENV SECRET_KEY=fail_if_run
ENV TWILIO_TOKEN=fail_if_run

# Build frontent
WORKDIR /root/santa/src
RUN ./manage.py collectstatic

# uwsgi
WORKDIR /root/santa
COPY ./uwsgi.ini ./uwsgi.ini 

# Copy setting.py again for build cache
COPY  ./src/santa/settings.py ./src/santa/settings.py

# Entry migrate and start
RUN mkdir -p /mnt/databases/santa/
EXPOSE 8080
COPY ./docker_entrypoint.sh ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh
