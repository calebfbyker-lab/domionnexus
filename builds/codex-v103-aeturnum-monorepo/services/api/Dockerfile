FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../../packages ./packages
COPY . .
ENV PYTHONPATH=/app/packages/core/src:/app/packages/neuro/src
EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
