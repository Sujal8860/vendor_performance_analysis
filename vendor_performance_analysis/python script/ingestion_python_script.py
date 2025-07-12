import os
import pandas as pd
from sqlalchemy import create_engine
import logging
import time

# Set paths
data_dir = "C:/Users/ASUS 1/project/data"
log_dir = "C:/Users/ASUS 1/project/logs"
db_path = "C:/Users/ASUS 1/project/inventory.db"

# Create logs directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=os.path.join(log_dir, "ingestion_db.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# Connect to database
engine = create_engine(f"sqlite:///{db_path}")

def ingest_db_chunked(file_path, table_name, engine, chunksize=10000):
    """Ingest CSV file in chunks and estimate progress"""
    try:
        total_rows = sum(1 for _ in open(file_path)) - 1  # -1 to exclude header
        total_chunks = (total_rows // chunksize) + 1
        print(f"📦 Total Rows: {total_rows} | Chunk Size: {chunksize} | Total Chunks: {total_chunks}")

        start = time.time()
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize)):
            chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
            elapsed = time.time() - start
            avg_time_per_chunk = elapsed / (i + 1)
            est_remaining = avg_time_per_chunk * (total_chunks - (i + 1))
            print(f"✅ Chunk {i+1}/{total_chunks} inserted | ⏱ Estimated time left: {est_remaining:.2f} seconds")
            logging.info(f"Chunk {i+1} inserted into {table_name}")
    except Exception as e:
        logging.error(f"❌ Error ingesting {table_name}: {e}")
        print(f"❌ Error in {table_name}: {e}")

def load_data():
    """Load all CSV files from data directory and ingest into DB"""
    start_all = time.time()
    print(f"📁 Checking files in: {data_dir}")

    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            file_path = os.path.join(data_dir, file)
            table_name = file[:-4]
            print(f"\n🚀 Processing: {file}")
            ingest_db_chunked(file_path, table_name, engine)
            logging.info(f"{file} ingested into {table_name}")
    
    end_all = time.time()
    print(f"\n🎉 All files processed in {(end_all - start_all)/60:.2f} minutes")
    logging.info("✅ All ingestion completed.")

# Run the function
if __name__ == "__main__":
    load_data()
