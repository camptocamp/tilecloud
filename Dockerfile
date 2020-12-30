FROM osgeo/gdal:3.2.0

RUN apt update
RUN apt install --yes python3-wheel python3-setuptools python3-pip libpq-dev
RUN python3 -m pip install Cython

WORKDIR /app

COPY requirements-dev.txt ./
RUN python3 -m pip install --requirement=requirements-dev.txt

COPY requirements.txt ./
RUN python3 -m pip install --requirement=requirements.txt
