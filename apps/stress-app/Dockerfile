FROM python:3.12-slim
WORKDIR /app
RUN pip install flask prometheus_client
COPY stress_api.py .
EXPOSE 8080
CMD ["python", "stress_api.py"]