FROM ubuntu:22.04

WORKDIR /work/server

COPY src /work/server/

RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get  clean

RUN pip install -r requirements.txt -i https://pypi.douban.com/simple


# CMD [ "/bin/bash", "/work/server/service.sh" ]
