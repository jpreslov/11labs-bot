FROM python:3.11.6
RUN apt update && apt install -y ffmpeg
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock .
RUN pip install poetry && poetry install --no-root --no-directory
COPY src/ ./src
RUN poetry install --no-dev

ENTRYPOINT ["poetry", "run", "python", "src/main.py"]
