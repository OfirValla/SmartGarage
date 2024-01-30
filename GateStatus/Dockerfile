FROM python:3.11-slim as base

RUN apt-get -y -V update 
RUN apt-get install -y -V ffmpeg 
RUN apt-get install -y -V libsm6 
RUN apt-get install -y -V libxext6 
RUN apt-get install -y -V iputils-ping

FROM python:3.11-slim as git-pull

RUN apt-get -y update && apt-get install -y git

WORKDIR /app
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/OfirValla/SmartGate.git && cd /app/SmartGate && git pull

FROM base as final

WORKDIR /app
COPY --from=git-pull /app/SmartGate/GateStatus .

RUN chmod +x /app/entrypoint.sh
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python3", "-u", "./main.py"]