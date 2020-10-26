FROM python:3.7

RUN apt-get update && apt-get install -y libpq-dev python3-dev telnet

WORKDIR /project
COPY project /project

RUN pip install -r requirements.txt

COPY cmd.sh /
CMD ["/cmd.sh"]