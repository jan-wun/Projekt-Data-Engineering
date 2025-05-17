FROM bitnami/spark:latest

USER root

RUN install_packages postgresql-client

COPY wait-for-table.sh /opt/wait-for-table.sh
RUN chmod +x /opt/wait-for-table.sh

USER 1001
