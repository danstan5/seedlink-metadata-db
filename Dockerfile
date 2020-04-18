FROM python:3.7

LABEL maintainer "Dan Stanton <danstan5@hotmail.co.uk>"

RUN apt-get update

COPY . . 

RUN pip install numpy
RUN pip install --no-cache-dir -r requirements.txt

ENV DB_HOST=localhost \
    DB_USERNAME=usr \
    DB_PASSWORD=pass

RUN chmod +x /docker-entrypoint.sh

CMD /docker-entrypoint.sh

# entrypoint runs without the shell
# ENTRYPOINT [ "/docker-entrypoint.sh" ]
