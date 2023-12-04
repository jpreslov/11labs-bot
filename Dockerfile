FROM python:3.11-slim

RUN python -m venv venv

COPY requirements.txt .

RUN . venv/bin/activate && venv/bin/python3 -m pip install -r requirements.txt

COPY src/main.py .
CMD . venv/bin/activate && exec venv/bin/python3 main.py
