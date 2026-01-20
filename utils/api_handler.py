import requests
import os


def fetch_all_products():
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get('products', [])

        print("API fetch successful")
        return products

    except requests.exceptions.RequestException:
        print("API fetch failed")
        return []

    except Exception:
        print("API processing failed")
        return []


def create_product_mapping(api_products):
    # Build a dictionary mapping product IDs to their info
    product_mapping = {}

    for product in api_products:
        product_id = product.get('id')

        if product_id is not None:
            product_mapping[product_id] = {
                'title': product.get('title', ''),
                'category': product.get('category', ''),
                'brand': product.get('brand', ''),
                'rating': product.get('rating', 0.0)
            }

    return product_mapping


def enrich_sales_data(transactions, product_mapping):
    enriched_transactions = []

    for transaction in transactions:
        enriched_transaction = transaction.copy()

        # Set defaults in case we can't find a match
        enriched_transaction['API_Category'] = None
        enriched_transaction['API_Brand'] = None
        enriched_transaction['API_Rating'] = None
        enriched_transaction['API_Match'] = False

        try:
            product_id_str = transaction.get('ProductID', '')

            # Extract numeric ID from ProductID (e.g., P101 -> 101)
            if product_id_str.startswith('P'):
                numeric_id = int(product_id_str[1:])

                # If we found a match in the API data, add the info
                if numeric_id in product_mapping:
                    api_info = product_mapping[numeric_id]
                    enriched_transaction['API_Category'] = api_info.get('category')
                    enriched_transaction['API_Brand'] = api_info.get('brand')
                    enriched_transaction['API_Rating'] = api_info.get('rating')
                    enriched_transaction['API_Match'] = True

        except Exception:
            pass

        enriched_transactions.append(enriched_transaction)

    return enriched_transactions


def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    # Create directory if it doesn't exist
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region',
        'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
    ]

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('|'.join(header) + '\n')

            for transaction in enriched_transactions:
                row = []
                for field in header:
                    value = transaction.get(field)

                    # Handle None values as empty strings
                    if value is None:
                        row.append('')
                    else:
                        row.append(str(value))

                file.write('|'.join(row) + '\n')

    except Exception:
        print("Failed to save enriched data")
