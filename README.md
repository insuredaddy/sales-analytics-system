# Sales Analytics Assignment

This project is part of my Business Analytics certificate course.  
It processes a raw sales file, cleans and validates the data, enriches it using an external API, and generates a text report with basic sales insights.

## What the program does

- Reads a pipe-delimited sales file  
- Cleans and parses transactions  
- Validates bad records (quantity, price, missing fields, ID formats)  
- Allows optional filtering by region and transaction amount  
- Fetches product data from a public API  
- Enriches sales records with API data  
- Saves enriched data to a file  
- Generates a formatted text report with:
  - Overall revenue
  - Region-wise sales
  - Top products and customers
  - Daily sales trend
  - Low-performing products
  - API enrichment summary

## How to run

1. Install dependencies  

```bash
pip install -r requirements.txt
```

2. Run the program  

```bash
python main.py
```

3. Output files created  
- `data/enriched_sales_data.txt`  
- `output/sales_report.txt`

## Notes

- The API used is DummyJSON (products 1–100).  
- The sales file uses product IDs starting from P101, so API matches are expected to be false.  
- This behavior is intentional and verified during testing.
