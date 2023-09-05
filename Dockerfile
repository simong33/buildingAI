FROM python:3.10.6-buster

WORKDIR /prod

COPY requirements_prod.txt requirements_prod.txt
RUN pip install --upgrade pip && \
    pip install -r requirements_prod.txt

USER root

RUN useradd -ms /bin/bash newuser && \
    mkdir -p /home/newuser/.lewagon/mlops/preproc && \
    mkdir -p /home/newuser/.lewagon/mlops/encoders

RUN chown -R newuser:newuser /prod && \
    chown -R newuser:newuser /home/newuser/.lewagon

USER newuser

COPY app app
COPY setup.py Makefile buildingai.json /prod/

RUN pip install . && \
    make reset_local_files

CMD uvicorn app.api.fast:app --host 0.0.0.0 --port $PORT
