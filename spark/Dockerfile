FROM bitnami/spark:latest

USER root

RUN install_packages postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-table.sh /opt/wait-for-table.sh
RUN chmod +x /opt/wait-for-table.sh

USER 1001
