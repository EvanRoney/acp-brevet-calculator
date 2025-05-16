FROM python:3.8
ADD . /todo
WORKDIR /todo
RUN pip install -r requirements.txt

