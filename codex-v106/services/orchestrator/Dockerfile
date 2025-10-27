FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/../..:/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8010
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8010"]
