FROM python:3.9
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED 1

CMD ["python", "serve_map_from_elastic.py"]
