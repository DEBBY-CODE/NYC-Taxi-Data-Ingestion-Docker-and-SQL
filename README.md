# NYC-Taxi-Data-Ingestion-and Analysis Using SQL

## Project Overview 
This project focuses on setting up an environment with Docker, PostgreSQL, PgAdmin, and Python and leveraging these tools to create a data ingestion pipeline that moves data from CSV files hosted in a GitHub repo into a database , perform analysis on the data to gain insights on trip data and then deploy infrastructure using Terraform. 
This README file provides guidelines and SQL queries to solve the required questions.


## Postgres Set Up With Docker 
### Docker Volume
Create a Docker volume by running the docker command below:\
This creates a volume in Docker to host your data so that your files are saved in your database even when you leave the Docker container. As Docker does not take a snapshot of the state of your files, you must create this volume file, which is then mapped to Postgres inside the container. Postgres will store our data in this volume file, ensuring that data is not lost even when we restart Docker.
``` ubuntu
docker volume create --name ny_taxi_posgres_volume_local -d local
```

### PostgreSQL Docker Container
Run the command below to start your PostgreSQL container inside docker: \
The commands used -e to set environment variables, -v creates a volume to store data even if the container stops working, -p creates a flag that maps port 5432 from your host computer 

``` ubuntu
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

### PgAdmin Docker Container
Run the docker command to launch a pgAdmin container, which is a convenient graphical interface to interact with our  PostgreSQL database 

``` ubuntu
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4
 
```

### Building the Data Pipeline
Build a docker image for the data pipeline

``` ubuntu
docker build -t taxi_ingest:v001 .
```
Run the docker container for the data ingestion pipeline.

```ubuntu
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=green_taxi_trips \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

``` ubuntu

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pg-database \
  --port=5432 \
  --db=ny_taxi \
  --table_name=taxi_zone_lookup \
  --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

```

### Using Docker Compose

Deploying the entire containers used
```ubuntu
docker-compose up
```

Detached mode
```ubuntu
docker-compose up -d
```

Stopping the containers 
``` ubuntu
docker-compose down
```

## Setting Up Terraform

## GCP and Big Query Deployment
