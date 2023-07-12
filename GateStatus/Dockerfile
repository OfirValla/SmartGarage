FROM python:3.11-slim as base

RUN apt-get -y update && apt-get install -y ffmpeg 
RUN apt-get install -y libsm6 
RUN apt-get install -y libxext6 
RUN apt-get install -y iputils-ping
RUN apt-get install -y git

FROM python:3.11-slim as git-pull

WORKDIR /app
RUN git clone https://github.com/OfirValla/GateOpener.git
WORKDIR /app/GateOpener
RUN git pull

FROM base as final

WORKDIR /app
COPY --from=git-pull /app/GateController/GateStatus .

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "./main.py"]