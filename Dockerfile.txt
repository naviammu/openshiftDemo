FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY app.py /app/
RUN pip install --no-cache-dir Flask==3.0.3

EXPOSE 8080
CMD ["python", "app.py"]
