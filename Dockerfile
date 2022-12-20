FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

RUN apt update && \
    apt install -y default-mysql-client

COPY . /srv/root
WORKDIR /srv/root

EXPOSE 80

CMD ["/srv/root/main.py"]
