FROM python:3-alpine3.11
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
EXPOSE 8000
CMD gunicorn --worker-class eventlet -w 1 app:app