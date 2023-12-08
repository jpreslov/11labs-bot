FROM python:3.11.6

WORKDIR /app

RUN apt-get update  \
  && apt-get install -y build-essential libffi-dev python3-dev

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python3 main.py
