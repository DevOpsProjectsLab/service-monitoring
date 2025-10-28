FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m python

COPY . .
RUN chown -R python:python /app

USER python

EXPOSE 8000
CMD ["python", "app.py"]