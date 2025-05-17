FROM python:3.10-slim

USER root

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-table.sh /opt/wait-for-table.sh
RUN chmod +x /opt/wait-for-table.sh

COPY app.py .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
