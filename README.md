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
Run the docker container for the data ingestion pipeline for two containers for each csv file since we have multiple files. However, an efficient way to do this would be to use docker-compose in the next section.

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

Create docker compose yaml file 

``` ubuntu
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"

taxi_ingest:
    image: taxi_ingest:v001
    build:
      context: .
    depends_on:
      - pgdatabase
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_HOST=pgdatabase
      - POSTGRES_PORT=5432
      - POSTGRES_DB=ny_taxi
    command: >
      sh -c "
      python ingest_data.py --user=root --password=root --host=pgdatabase --port=5432 --db=ny_taxi --table_name=green_taxi_trips --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz &&
      python ingest_data.py --user=root --password=root --host=pgdatabase --port=5432 --db=ny_taxi --table_name=taxi_zone_lookup --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
volumes:
  ny_taxi_postgres_data:
    external: true
```

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

## Answers to Docker , SQL Query Analysis and Terraform Questions : 
### Question 1. Understanding docker first run
Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.
What's the version of pip in the image?
![Q1](https://github.com/user-attachments/assets/aec9e63b-0d46-4573-ad0e-edb0292c9b5c)

### Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?
```docker
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```
![Q 2](https://github.com/user-attachments/assets/d54922a3-c863-4d3c-9ce5-17cdd76d2474)


### Question 3. Trip Segmentation Count
During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:

1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles


![Q 3](https://github.com/user-attachments/assets/1def7b82-dbda-4d2b-b365-65a2b135a7a4)


### Question 4. Longest trip for each day
Which was the pickup day with the longest trip distance? Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance.
![Q 4](https://github.com/user-attachments/assets/e47268d0-1bde-4ebb-aa2a-684e0455edef)


### Question 5. Three biggest pickup zones
Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?

Consider only lpep_pickup_datetime when filtering by date.
![Q5](https://github.com/user-attachments/assets/577851b6-59d0-41a2-97cc-b8dffcbb5247)

### Question 6. Largest tip

For the passengers picked up in October 2019 in the zone name "East Harlem North" which was the drop off zone that had the largest tip?

Note: it's tip, not trip

We need the name of the zone, not the ID.
![Q6](https://github.com/user-attachments/assets/bc71ee39-33ec-4d38-9931-37259cfc29cc)


### Question 7. Terraform Workflow


