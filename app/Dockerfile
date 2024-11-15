FROM python:3.10-slim

RUN mkdir app
WORKDIR app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/
CMD python app.py