# syntax=docker/dockerfile:1

FROM python:3.9.2

WORKDIR /home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia

COPY requierments.txt requierments.txt
RUN pip3 install -r requierments.txt

COPY . .

CMD [ "python3", "./Jadzia.py"]



