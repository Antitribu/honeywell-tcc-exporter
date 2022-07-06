FROM debian:latest
USER root

ENV DEBIAN_FRONTEND noninteractive

ADD requirements/packages-deb.txt /etc/packages-deb.txt
RUN apt-get update && apt-get upgrade -qy && apt-get -y install $(cat /etc/packages-deb.txt)

ADD requirements/packages-pip.txt /etc/packages-pip.txt
RUN pip3 install -r /etc/packages-pip.txt

RUN cd /opt && git clone https://github.com/watchforstock/evohome-client.git
RUN pip3 install /opt/evohome-client/

RUN mkdir /app
ADD exporter.py /app/exporter.py

ENTRYPOINT ["/app/exporter.py"]
