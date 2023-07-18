FROM python:3.11-slim as git-pull

RUN apt-get -y update && apt-get install -y git

WORKDIR /app
RUN git clone https://github.com/OfirValla/GateController.git && cd /app/GateController && git pull

FROM python:3.11 as final

WORKDIR /app
COPY --from=git-pull /app/GateController/GateController .

#RUN apt-get -y install gcc
RUN pip3 install setuptools rpi.gpio
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "./main.py"]