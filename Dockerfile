FROM python:3.12-slim
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction
COPY . .
EXPOSE 5050
CMD ["python", "main.py"]
