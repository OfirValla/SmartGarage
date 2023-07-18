FROM python:3.11-slim as git-pull

RUN apt-get -y update && apt-get install -y git

WORKDIR /app
RUN git clone https://github.com/OfirValla/GateController.git
WORKDIR /app/GateController
RUN git pull

FROM python:3.11-slim as final

WORKDIR /app
COPY --from=git-pull /app/GateController/GateOpener .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "./main.py"]