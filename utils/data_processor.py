def parse_transactions(raw_lines):
    transactions = []
    expected_fields = 8

    for line in raw_lines:
        if not line.strip():
            continue

        fields = line.split('|')

        # Skip rows that don't have the right number of fields
        if len(fields) != expected_fields:
            continue

        try:
            transaction_id = fields[0].strip()
            date = fields[1].strip()
            product_id = fields[2].strip()
            product_name = fields[3].strip().replace(',', '')

            quantity_str = fields[4].strip().replace(',', '')
            unit_price_str = fields[5].strip().replace(',', '')

            customer_id = fields[6].strip()
            region = fields[7].strip()

            # Simple check to avoid bad rows with empty numbers
            if not quantity_str or not unit_price_str:
                continue

            quantity = int(quantity_str)
            unit_price = float(unit_price_str)

            transaction = {
                'TransactionID': transaction_id,
                'Date': date,
                'ProductID': product_id,
                'ProductName': product_name,
                'Quantity': quantity,
                'UnitPrice': unit_price,
                'CustomerID': customer_id,
                'Region': region
            }

            transactions.append(transaction)

        except (ValueError, IndexError):
            continue

    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    required_fields = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region'
    ]

    total_input = len(transactions)
    valid_transactions = []
    invalid_count = 0

    for tx in transactions:
        # Check if all required fields are present and not empty
        if not all(field in tx and tx[field] not in (None, '') for field in required_fields):
            invalid_count += 1
            continue

        # Can't have zero or negative quantities/prices
        if tx['Quantity'] <= 0 or tx['UnitPrice'] <= 0:
            invalid_count += 1
            continue

        # IDs need to start with the right letter
        if not tx['TransactionID'].startswith('T'):
            invalid_count += 1
            continue

        if not tx['ProductID'].startswith('P'):
            invalid_count += 1
            continue

        if not tx['CustomerID'].startswith('C'):
            invalid_count += 1
            continue

        valid_transactions.append(tx)

    # Show what regions and amounts are available
    regions = sorted(set(t['Region'] for t in valid_transactions))
    print("Available regions:", regions)

    amounts = [t['Quantity'] * t['UnitPrice'] for t in valid_transactions]
    if amounts:
        print("Transaction amount range:", min(amounts), "-", max(amounts))
    else:
        print("Transaction amount range: 0 - 0")

    filtered_by_region = 0
    filtered_by_amount = 0

    filtered = valid_transactions

    if region:
        before = len(filtered)
        filtered = [t for t in filtered if t['Region'] == region]
        filtered_by_region = before - len(filtered)
        print("Records after region filter:", len(filtered))

    if min_amount is not None or max_amount is not None:
        before = len(filtered)
        temp = []
        for t in filtered:
            amount = t['Quantity'] * t['UnitPrice']
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue
            temp.append(t)

        filtered = temp
        filtered_by_amount = before - len(filtered)
        print("Records after amount filter:", len(filtered))

    filter_summary = {
        'total_input': total_input,
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered)
    }

    return filtered, invalid_count, filter_summary


def calculate_total_revenue(transactions):
    total_revenue = 0.0

    for transaction in transactions:
        total_revenue += transaction['Quantity'] * transaction['UnitPrice']

    return total_revenue


def region_wise_sales(transactions):
    total_revenue = calculate_total_revenue(transactions)

    region_stats = {}

    for transaction in transactions:
        region = transaction['Region']
        sales_amount = transaction['Quantity'] * transaction['UnitPrice']

        if region not in region_stats:
            region_stats[region] = {
                'total_sales': 0.0,
                'transaction_count': 0,
                'percentage': 0.0
            }

        region_stats[region]['total_sales'] += sales_amount
        region_stats[region]['transaction_count'] += 1

    # Calculate percentages
    for region in region_stats:
        if total_revenue > 0:
            region_stats[region]['percentage'] = (
                region_stats[region]['total_sales'] / total_revenue
            ) * 100
        else:
            region_stats[region]['percentage'] = 0.0

    # Sort by sales amount, highest first
    sorted_regions = sorted(
        region_stats.items(),
        key=lambda x: x[1]['total_sales'],
        reverse=True
    )

    result = {}
    for region, stats in sorted_regions:
        result[region] = stats

    return result


def top_selling_products(transactions, n=5):
    product_stats = {}

    for transaction in transactions:
        product_name = transaction['ProductName']
        quantity = transaction['Quantity']
        unit_price = transaction['UnitPrice']
        revenue = quantity * unit_price

        if product_name not in product_stats:
            product_stats[product_name] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_stats[product_name]['total_quantity'] += quantity
        product_stats[product_name]['total_revenue'] += revenue

    # Sort by quantity sold, highest first
    sorted_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]['total_quantity'],
        reverse=True
    )

    result = []
    for product_name, stats in sorted_products[:n]:
        result.append((
            product_name,
            stats['total_quantity'],
            stats['total_revenue']
        ))

    return result


def customer_analysis(transactions):
    customer_stats = {}

    for transaction in transactions:
        customer_id = transaction['CustomerID']
        product_name = transaction['ProductName']
        quantity = transaction['Quantity']
        unit_price = transaction['UnitPrice']
        amount_spent = quantity * unit_price

        if customer_id not in customer_stats:
            customer_stats[customer_id] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }

        customer_stats[customer_id]['total_spent'] += amount_spent
        customer_stats[customer_id]['purchase_count'] += 1
        customer_stats[customer_id]['products_bought'].add(product_name)

    # Calculate average order value and convert sets to lists
    for customer_id in customer_stats:
        stats = customer_stats[customer_id]
        if stats['purchase_count'] > 0:
            stats['avg_order_value'] = stats['total_spent'] / stats['purchase_count']
        else:
            stats['avg_order_value'] = 0.0
        stats['products_bought'] = sorted(list(stats['products_bought']))

    # Sort by total spent, highest first
    sorted_customers = sorted(
        customer_stats.items(),
        key=lambda x: x[1]['total_spent'],
        reverse=True
    )

    result = {}
    for customer_id, stats in sorted_customers:
        result[customer_id] = stats

    return result


def daily_sales_trend(transactions):
    daily_stats = {}

    for transaction in transactions:
        date = transaction['Date']
        customer_id = transaction['CustomerID']
        quantity = transaction['Quantity']
        unit_price = transaction['UnitPrice']
        revenue = quantity * unit_price

        if date not in daily_stats:
            daily_stats[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'unique_customers': set()
            }

        daily_stats[date]['revenue'] += revenue
        daily_stats[date]['transaction_count'] += 1
        daily_stats[date]['unique_customers'].add(customer_id)

    # Sort by date and convert sets to counts
    result = {}
    sorted_dates = sorted(daily_stats.keys())

    for date in sorted_dates:
        stats = daily_stats[date]
        result[date] = {
            'revenue': stats['revenue'],
            'transaction_count': stats['transaction_count'],
            'unique_customers': len(stats['unique_customers'])
        }

    return result


def find_peak_sales_day(transactions):
    daily_stats = {}

    for transaction in transactions:
        date = transaction['Date']
        quantity = transaction['Quantity']
        unit_price = transaction['UnitPrice']
        revenue = quantity * unit_price

        if date not in daily_stats:
            daily_stats[date] = {
                'revenue': 0.0,
                'transaction_count': 0
            }

        daily_stats[date]['revenue'] += revenue
        daily_stats[date]['transaction_count'] += 1

    # Find the day with highest revenue
    peak_date = None
    peak_revenue = 0.0
    peak_transaction_count = 0

    for date, stats in daily_stats.items():
        if stats['revenue'] > peak_revenue:
            peak_revenue = stats['revenue']
            peak_date = date
            peak_transaction_count = stats['transaction_count']

    if peak_date is None:
        return (None, 0.0, 0)

    return (peak_date, peak_revenue, peak_transaction_count)


def low_performing_products(transactions, threshold=10):
    product_stats = {}

    for transaction in transactions:
        product_name = transaction['ProductName']
        quantity = transaction['Quantity']
        unit_price = transaction['UnitPrice']
        revenue = quantity * unit_price

        if product_name not in product_stats:
            product_stats[product_name] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_stats[product_name]['total_quantity'] += quantity
        product_stats[product_name]['total_revenue'] += revenue

    # Find products with total quantity below threshold
    low_performing = []
    for product_name, stats in product_stats.items():
        if stats['total_quantity'] < threshold:
            low_performing.append((
                product_name,
                stats['total_quantity'],
                stats['total_revenue']
            ))

    # Sort by quantity, lowest first
    low_performing.sort(key=lambda x: x[1])

    return low_performing
