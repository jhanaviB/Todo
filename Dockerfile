FROM python:3.10

RUN apt-get update
RUN apt-get install -y --no-install-recommends
EXPOSE 8081
EXPOSE 6379
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
CMD python3 app.py