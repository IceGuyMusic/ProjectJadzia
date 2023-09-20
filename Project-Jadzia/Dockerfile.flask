FROM python:3.9-buster 

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=Jadzia.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

