FROM python:3.11-alpine

# RUN apk add ffmpeg

RUN python -m venv venv

COPY requirements.txt .

RUN . venv/bin/activate && venv/bin/python3 -m pip install -r requirements.txt

COPY src/main.py .

#EXPOSE 80/udp

CMD . venv/bin/activate && exec venv/bin/python3 main.py
