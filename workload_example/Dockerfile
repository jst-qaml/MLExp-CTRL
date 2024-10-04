FROM python:3
RUN apt update && apt install -y sudo git vim
RUN pip3 install dvc dvc-s3

ARG UID=1003
RUN groupadd -g ${UID} qaml && \
    useradd -m -s /bin/bash -u ${UID} -g ${UID} -G sudo qaml && \
    echo "qaml ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/qaml
USER qaml
COPY ./example/ ./
