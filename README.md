# vendor_performance_analysis
## 🔄 End to End ETL & Analytics Pipeline

### 1. Define Business Problem
Effective inventory and sales management are critical for optimizing profitability in the retail and wholesale industry. Companies need to ensure that they are not incurring losses due to inefficient pricing, poor inventory turnover, or vendor dependency.  
The goal of this analysis is to:
- Identify underperforming brands that require promotional or pricing adjustments.  
- Determine top vendors contributing to sales and gross profit.  
- Analyze the impact of bulk purchasing on unit costs.  
- Assess inventory turnover to reduce holding costs and improve efficiency.  
- Investigate the profitability variance between high‑performing and low‑performing vendors.  

---

### 2. Extract & Explore
- **Data Source:** Multiple raw CSVs (purchases, sales, vendor invoices, price lists) consolidated into a single SQLite database.  
- **Table Exploration:** Schemas inspected to understand relationships between `VendorNumber`, `Brand`, pricing fields, quantities, and costs.  
- **Initial Observations:**  
  - High skewness in numeric fields.  
  - Freight cost showed slab‑based distribution patterns.  
  - Large variance between listed vs actual purchase prices.  

---

### 3. Transform (SQL Powered)
- **Merge & Aggregate:**  
  - Joined sales, purchases, and vendor details using `VendorNumber` and `Brand`.  
  - Aggregated KPIs like `TotalSalesDollars`, `TotalPurchaseDollars`, `GrossProfit`, and `StockTurnover`.  
- **Cleanse:**  
  - Removed 0‑sales and loss‑making records (where `GrossProfit <= 0` or `ProfitMargin <= 0`) to focus on actionable data.  
- **Feature Engineering:**  
  - `GrossProfit = TotalSalesDollars − TotalPurchaseDollars`  
  - `ProfitMargin = GrossProfit ÷ TotalSalesDollars` (%)  
  - `StockTurnover = SalesQuantity ÷ PurchaseQuantity`  
  - `SalesToPurchaseRatio = SalesDollars ÷ PurchaseDollars`  
  - `UnitPurchasePrice = PurchaseDollars ÷ PurchaseQuantity`  

---

### 4. 🧠 Load

This phase handles ingestion of raw CSV files and transformation of the data into a clean, structured format for analysis and dashboarding.

#### 🔹 Script 1 – Ingestion with Chunking (`ingestion_script.py`)

- Efficiently loads large CSV files (~millions of rows) from the `/data/` folder into an SQLite database using chunked processing via pandas.
- Implements **dynamic table creation**, logs chunk-wise progress, and estimates **remaining time** for ingestion.
- Logs every important step to `logs/ingestion_db.log`.

#### 🔹 Script 2 – Vendor Summary Generation (`vendor_summary_script.py`)

- Merges and aggregates key datasets: `purchases`, `sales`, `vendor_invoice`, and `purchase_prices` using optimized SQL queries with `WITH` statements.
- Calculates essential KPIs:
  - `gross_profit`, `profit_margin`, `stock_turnover`, `sales_to_purchase_ratio`
- Cleans missing values, strips text fields, and filters out irrelevant or loss-making records.
- Saves the final cleaned and feature-rich summary into both:
  - a new table in the SQLite database (`vendor_sales_summary`)
  - a CSV file for external analysis

#### 🗂 Version Control

- All ETL scripts are stored under the `scripts/` folder for reproducibility and easy maintenance.
- Logging and modular code structure make reruns scalable and audit-friendly.


---

### 🔍 5. Exploratory Data Analysis (Python + Notebook)
- **Notebook Setup:**  
  - Used pandas, NumPy, seaborn, and matplotlib under a dark‑themed custom visual style.  
  - Applied a dollar‑formatting function to all monetary metrics for readability (e.g., `$2.1M`, `$10.5K`).  
- **Data Validation & Sanity Checks:**  
  - Confirmed data consistency across joins, especially between purchase and sales tables.  
  - Verified that all `vendorname`, `brand`, and `description` fields were properly mapped.  
  - Calculated unit price variance and detected missing or abnormal profit margins.  
- **Descriptive Statistics:**  
  - Found high skewness in `TotalSalesDollars` and `GrossProfit`, with a long tail of underperforming vendors.  
  - Top 10 vendors contributed **65.69%** of the total purchase dollars.  
  - Top‑performing brands sometimes had lower margins than low‑volume niche brands.  
  - Identified a massive **\$2.71 M** in unsold inventory, locked across low‑turnover vendors.  
- **Statistical Relationships:**  
  - `TotalSalesQuantity` vs. `TotalPurchaseQuantity` had a Pearson correlation of **0.999**, indicating highly efficient inventory usage.  
  - Boxplots revealed that “Large” order sizes reduce unit cost by up to **72%** compared to “Small” orders.  
- **Risk & Efficiency KPIs:**  
  - **Stock Turnover < 1:** Flagged vendors with slow‑moving stock.  
  - Vendors like Tamworth Distilling, Walpole Winery, and Sweetwater Farm had lowest turnover — suggesting poor inventory flow.  
  - Pareto analysis showed that just 10 vendors account for the majority of procurement — increasing dependency risk.  
- **Profitability Insights:**  
  - Calculated 95% confidence intervals for `ProfitMargin`:  
    - Top vendors: CI = (30.74%, 31.61%)  
    - Low vendors: CI = (40.48%, 42.62%)  
    - Highlights that low‑performing vendors have significantly higher margins, likely due to premium pricing or niche offerings.  
  - Hypothesis testing via t‑test showed the difference in margins is statistically significant (p < 0.05).  
- **Key Visuals Used:**  
  - Horizontal bar charts with in‑bar labels for readability.  
  - Pareto chart (bar + cumulative line) for purchase contribution.  
  - Donut chart showing vendor dependency.  
  - Boxplots and scatterplots to capture pricing and margin behavior.  
  - Histogram overlaid with confidence intervals for statistical visuals.  

---

### 6. Dashboarding & Reporting
- **Power BI Dashboard** (single‑page `.pbix`; data refresh ~ 3 min)  
- **KPI Cards:**  
  1. Total Sales: \$ 441.41 M  
  2. Total Purchases: \$ 307.34 M  
  3. Gross Profit: \$ 134.07 M  
  4. Avg Profit Margin: 38.72 %  
  5. Unsold Capital: \$ 2.71 M  
- **Visuals (all on one canvas):**  
  - **Donut Chart** (Purchase Contribution %): Top 10 vendors vs “Others” (e.g., Diageo North America 16.3 %, Others combined).  
  - **Bar Chart** (Top Vendors by Sales): Shows the top 10, cumulatively capturing ~ 65 % of total sales.  
  - **Bar Chart** (Top Brands by Sales): Leading 10 brands (Jack Daniels \$ 8.0 M, Tito’s Handcrafted \$ 7.4 M, etc.).  
  - **Bar Chart** (Low Performing Vendors): Bottom 5 vendors by Avg Stock Turnover (0.62×–0.77×).  
  - **Scatter Plot** (Low Performing Brands): Plots `TotalSales` vs `AvgProfitMargin` for ~ 198 brands; “Target” brands flagged in red.  
- **Interactivity:**  
  - **Tooltips:** Hover reveals a mini‑matrix of four fields — Brand Description, `TargetBrand` flag (Yes/No), `TotalSales` (in M), and `AvgProfitMargin` (%).  
 
- **Executive Report (PDF):**  
  - Final summary included vendor rankings, bulk pricing benefits, inventory risks, and performance outliers, etc.  
  - Hypothesis testing section explained vendor profitability statistically.  

---

## 📈 Business Impact
- **Cost Optimization:** Found **72%** unit cost reduction opportunity via large orders.  
- **Inventory Strategy:** Identified **\$2.71 M** in unsold inventory for corrective actions.  
- **Vendor Risk Management:** Revealed **65.69%** vendor dependency, recommending supplier diversification.  
- **Strategic Profitability:** Helped identify premium brands with lower sales but higher margins for promotion.  
