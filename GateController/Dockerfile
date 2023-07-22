FROM python:3.11-slim as git-pull

ARG TZ
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y git

WORKDIR /app
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/OfirValla/SmartGate.git 

FROM python:3.11 as final

WORKDIR /app
COPY --from=git-pull /app/SmartGate/GateController .

RUN pip3 install setuptools rpi.gpio
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "./main.py"]