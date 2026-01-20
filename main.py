from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)
from utils.report_generator import generate_sales_report


def main():
    print("Reading sales data...")
    raw_lines = read_sales_data("data/sales_data.txt")
    print(f"Loaded {len(raw_lines)} rows")

    print("Parsing transactions...")
    transactions = parse_transactions(raw_lines)
    print(f"Parsed {len(transactions)} records")

    # Show available regions and amount range
    regions = sorted(set(t["Region"] for t in transactions if t.get("Region")))
    amounts = [t["Quantity"] * t["UnitPrice"] for t in transactions if t["Quantity"] > 0 and t["UnitPrice"] > 0]

    if regions:
        print("Regions:", ", ".join(regions))
    if amounts:
        print("Amount Range:", int(min(amounts)), "-", int(max(amounts)))

    filter_region = None
    filter_min_amount = None
    filter_max_amount = None

    choice = input("Filter data? [y/n]: ").strip().lower()
    if choice == "y":
        region_input = input("Region (Enter to skip): ").strip()
        if region_input:
            filter_region = region_input

        min_input = input("Min amount (Enter to skip): ").strip()
        if min_input:
            filter_min_amount = float(min_input)

        max_input = input("Max amount (Enter to skip): ").strip()
        if max_input:
            filter_max_amount = float(max_input)

    print("Validating transactions...")
    valid_transactions, invalid_count, _ = validate_and_filter(
        transactions,
        region=filter_region,
        min_amount=filter_min_amount,
        max_amount=filter_max_amount
    )
    print(f"Valid: {len(valid_transactions)}, Invalid: {invalid_count}")

    print("Fetching product data from API...")
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)
    print(f"Enriched {len(enriched_transactions)} transactions")

    print("Saving enriched data...")
    save_enriched_data(enriched_transactions, "data/enriched_sales_data.txt")

    print("Generating report...")
    generate_sales_report(valid_transactions, enriched_transactions, "output/sales_report.txt")

    print("Process finished.")


if __name__ == "__main__":
    main()
