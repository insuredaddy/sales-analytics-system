import os
from datetime import datetime
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)


def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    # Create output directory if needed
    directory = os.path.dirname(output_file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0.0

    dates = sorted(set(t['Date'] for t in transactions))
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    region_sales = region_wise_sales(transactions)
    top_products = top_selling_products(transactions, n=5)

    customer_stats = customer_analysis(transactions)
    top_customers = list(customer_stats.items())[:5]

    daily_trend = daily_sales_trend(transactions)
    peak_day = find_peak_sales_day(transactions)

    low_products = low_performing_products(transactions, threshold=10)

    # Calculate average transaction value per region
    region_avg = {}
    for region, stats in region_sales.items():
        if stats['transaction_count'] > 0:
            region_avg[region] = stats['total_sales'] / stats['transaction_count']

    # Count how many products were successfully enriched
    successful_enrichments = sum(1 for t in enriched_transactions if t.get('API_Match', False))
    total_enriched = successful_enrichments
    success_rate = (successful_enrichments / total_transactions * 100) if total_transactions > 0 else 0.0

    failed_products = sorted(
        set(t.get('ProductName') for t in enriched_transactions if not t.get('API_Match', False))
    )

    report_lines = []

    report_lines.append("=" * 44)
    report_lines.append("     SALES ANALYTICS REPORT")
    report_lines.append(f"     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"     Records Processed: {total_transactions}")
    report_lines.append("=" * 44)
    report_lines.append("")

    report_lines.append("OVERALL SUMMARY")
    report_lines.append("-" * 44)
    report_lines.append(f"Total Revenue:        {total_revenue:,.2f}")
    report_lines.append(f"Total Transactions:   {total_transactions}")
    report_lines.append(f"Average Order Value:  {avg_order_value:,.2f}")
    report_lines.append(f"Date Range:           {date_range}")
    report_lines.append("")

    report_lines.append("REGION-WISE PERFORMANCE")
    report_lines.append("-" * 44)
    report_lines.append(f"{'Region':<10} {'Sales':<15} {'% of Total':<12} {'Transactions':<12}")
    report_lines.append("-" * 44)
    for region, stats in region_sales.items():
        report_lines.append(
            f"{region:<10} {stats['total_sales']:,.2f}     {stats['percentage']:.2f}%      {stats['transaction_count']}"
        )
    report_lines.append("")

    report_lines.append("TOP 5 PRODUCTS")
    report_lines.append("-" * 44)
    report_lines.append(f"{'Rank':<6} {'Product Name':<20} {'Qty':<6} {'Revenue':<10}")
    report_lines.append("-" * 44)
    for rank, (product_name, qty, revenue) in enumerate(top_products, 1):
        report_lines.append(f"{rank:<6} {product_name:<20} {qty:<6} {revenue:,.2f}")
    report_lines.append("")

    report_lines.append("TOP 5 CUSTOMERS")
    report_lines.append("-" * 44)
    report_lines.append(f"{'Rank':<6} {'Customer ID':<15} {'Total Spent':<12} {'Orders':<8}")
    report_lines.append("-" * 44)
    for rank, (customer_id, stats) in enumerate(top_customers, 1):
        report_lines.append(
            f"{rank:<6} {customer_id:<15} {stats['total_spent']:,.2f}   {stats['purchase_count']}"
        )
    report_lines.append("")

    report_lines.append("DAILY SALES TREND")
    report_lines.append("-" * 44)
    report_lines.append(f"{'Date':<12} {'Revenue':<12} {'Txns':<8} {'Customers':<10}")
    report_lines.append("-" * 44)
    for date, stats in daily_trend.items():
        report_lines.append(
            f"{date:<12} {stats['revenue']:,.2f}   {stats['transaction_count']:<8} {stats['unique_customers']:<10}"
        )
    report_lines.append("")

    report_lines.append("PRODUCT PERFORMANCE ANALYSIS")
    report_lines.append("-" * 44)
    report_lines.append(
        f"Best Selling Day: {peak_day[0]} (Revenue: {peak_day[1]:,.2f}, Transactions: {peak_day[2]})"
    )
    report_lines.append("")

    if low_products:
        report_lines.append("Low Performing Products (Quantity < 10):")
        report_lines.append(f"{'Product Name':<20} {'Qty':<6} {'Revenue':<10}")
        report_lines.append("-" * 44)
        for name, qty, revenue in low_products:
            report_lines.append(f"{name:<20} {qty:<6} {revenue:,.2f}")
    else:
        report_lines.append("Low Performing Products: None")

    report_lines.append("")
    report_lines.append("Average Transaction Value per Region:")
    report_lines.append(f"{'Region':<10} {'Avg Value':<12}")
    report_lines.append("-" * 44)
    for region, avg_val in sorted(region_avg.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"{region:<10} {avg_val:,.2f}")
    report_lines.append("")

    report_lines.append("API ENRICHMENT SUMMARY")
    report_lines.append("-" * 44)
    report_lines.append(f"Total Products Enriched: {total_enriched}")
    report_lines.append(f"Success Rate:            {success_rate:.2f}%")
    report_lines.append("")

    if failed_products:
        report_lines.append("Products That Couldn't Be Enriched:")
        for name in failed_products:
            report_lines.append(f"  - {name}")
    else:
        report_lines.append("All products successfully enriched.")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        print(f"Report saved to {output_file}")
    except Exception:
        print("Failed to generate report")
