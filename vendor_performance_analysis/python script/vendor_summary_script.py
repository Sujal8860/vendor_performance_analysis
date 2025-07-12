# vendor_summary_script.py
# Purpose: Generate vendor-level summary table 

import os
import pandas as pd
import sqlite3
import logging
import time

# 🔧 Set paths (reusing from ingestion script)
db_path = "C:/Users/ASUS 1/project/inventory.db"
log_path = "C:/Users/ASUS 1/project/logs/vendor_summary_script.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# 🧾 Logging setup
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# 📦 Function to ingest final DataFrame into database
def ingest_to_db(df, table_name, conn):
    try:
        df.to_sql(table_name, con=conn, if_exists='replace', index=False)
        logging.info(f"✅ {table_name} ingested successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to ingest {table_name}: {e}")

# 📊 Step 1: Create vendor-level summary using SQL joins
def create_vendor_summary(conn):
    logging.info("🔍 Generating vendor summary using SQL joins")
    query = """
    WITH FreightSummary AS (
        SELECT VendorNumber, SUM(Freight) AS FreightCost
        FROM vendor_invoice
        GROUP BY VendorNumber
    ),
    PurchaseSummary AS (
        SELECT 
            p.VendorNumber,
            p.VendorName,
            p.Brand,
            p.Description,
            p.PurchasePrice,
            pp.Price AS ActualPrice,
            pp.Volume,
            SUM(p.Quantity) AS TotalPurchaseQuantity,
            SUM(p.Dollars) AS TotalPurchaseDollars
        FROM purchases p
        JOIN purchase_prices pp ON p.Brand = pp.Brand
        WHERE p.PurchasePrice > 0
        GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description, p.PurchasePrice, pp.Price, pp.Volume
    ),
    SalesSummary AS (
        SELECT 
            VendorNo,
            Brand,
            SUM(SalesQuantity) AS TotalSalesQuantity,
            SUM(SalesDollars) AS TotalSalesDollars,
            SUM(SalesPrice) AS TotalSalesPrice,
            SUM(ExciseTax) AS TotalExciseTax
        FROM sales
        GROUP BY VendorNo, Brand
    )
    SELECT 
        ps.VendorNumber,
        ps.VendorName,
        ps.Brand,
        ps.Description,
        ps.PurchasePrice,
        ps.ActualPrice,
        ps.Volume,
        ps.TotalPurchaseQuantity,
        ps.TotalPurchaseDollars,
        ss.TotalSalesQuantity,
        ss.TotalSalesDollars,
        ss.TotalSalesPrice,
        ss.TotalExciseTax,
        fs.FreightCost
    FROM PurchaseSummary ps
    LEFT JOIN SalesSummary ss ON ps.VendorNumber = ss.VendorNo AND ps.Brand = ss.Brand
    LEFT JOIN FreightSummary fs ON ps.VendorNumber = fs.VendorNumber
    ORDER BY ps.TotalPurchaseDollars DESC;
    """
    return pd.read_sql_query(query, conn)

# 🧼 Step 2: Clean and enhance the data
def clean_data(df):
    logging.info("🧽 Cleaning data and calculating KPIs")

    # Handle missing values and types
    df['Volume'] = df['Volume'].astype(float)
    df.fillna(0, inplace=True)
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    # ➕ KPIs or creating new column for better analysis
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']
    df['ProfitMargin'] = df.apply(lambda x: (x['GrossProfit'] / x['TotalSalesDollars'] * 100) if x['TotalSalesDollars'] else 0, axis=1)
    df['StockTurnover'] = df.apply(lambda x: (x['TotalSalesQuantity'] / x['TotalPurchaseQuantity']) if x['TotalPurchaseQuantity'] else 0, axis=1)
    df['SalesToPurchaseRatio'] = df.apply(lambda x: (x['TotalSalesDollars'] / x['TotalPurchaseDollars']) if x['TotalPurchaseDollars'] else 0, axis=1)

    return df

# 🚀 Run the full process
def main():
    start = time.time()
    logging.info("📁 Starting vendor summary script")

    conn = sqlite3.connect(db_path)
    df_summary = create_vendor_summary(conn)
    df_clean = clean_data(df_summary)
    ingest_to_db(df_clean, "vendor_sales_summary", conn)

    conn.close()
    elapsed = time.time() - start
    logging.info(f"🎯 Script completed in {elapsed:.2f} seconds")
    print(f"🎯 Script completed in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
