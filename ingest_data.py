from time import time
from sqlalchemy import create_engine, inspect
import pandas as pd
import argparse
import os

def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'output.csv'

    # Download the CSV file
    os.system(f"wget {url} -O {csv_name}")

    # Check if the file is gzip-compressed
    is_gzip = csv_name.endswith('.gz')

    # Create a database connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Skip ingestion if the table already exists
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' already exists in the database. Skipping ingestion for {url}.")
        return

    # Read and process the file
    if is_gzip:
        df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000, compression='gzip')
    else:
        df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Process the first chunk
    df = next(df_iter)
    if 'lpep_pickup_datetime' in df and 'lpep_dropoff_datetime' in df:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # Create the table and insert the first batch
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")
    df.to_sql(name=table_name, con=engine, if_exists="append")

    # Process remaining chunks
    while True:
        try:
            t_start = time()
            df = next(df_iter)
            if 'lpep_pickup_datetime' in df and 'lpep_dropoff_datetime' in df:
                df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
                df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists="append")
            t_end = time()
            print(f'Inserted another chunk... took {t_end - t_start:.3f} second(s)')
        except StopIteration:
            print(f"Finished ingesting data from {url} into {table_name}")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")
    parser.add_argument('--user', help="user name for postgres")
    parser.add_argument('--password', help="password for postgres")
    parser.add_argument('--host', help="host for postgres")
    parser.add_argument('--port', help="port for postgres")
    parser.add_argument('--db', help="database name for postgres")
    parser.add_argument('--table_name', help="name of the table where we will write the results to")
    parser.add_argument('--url', help="url of the CSV")
    args = parser.parse_args()

    main(args)
