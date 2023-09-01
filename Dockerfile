FROM python:3.10.6-buster

WORKDIR /prod

COPY app app
COPY requirements_prod.txt requirements_prod.txt
RUN pip install --upgrade pip
RUN pip install -r requirements_prod.txt

COPY setup.py setup.py
RUN pip install .

COPY Makefile Makefile
RUN make reset_local_files

CMD uvicorn app.api.fast:app --host 0.0.0.0 --port $PORT