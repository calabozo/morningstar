FROM python:3

RUN apt-get update && apt-get install -y --no-install-recommends \
    qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /opt
COPY src/ .

RUN pip install --no-cache-dir .

CMD [ "python",'download_forecast', "--out", "/mnt/forecast.csv" ]