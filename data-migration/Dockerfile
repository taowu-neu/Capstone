FROM postgres:14

# Install PostGIS client tools (optional, if needed for complex imports)
RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY import_csv.sh .

CMD ["bash", "/app/import_csv.sh"]