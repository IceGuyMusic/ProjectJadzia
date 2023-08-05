# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /Project-Jadzia

COPY requierments.txt requierments.txt
RUN pip install -r requierments.txt

COPY . .

CMD ["python3", "./Jadzia.py"]
