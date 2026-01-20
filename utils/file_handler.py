def read_sales_data(filename):
    # Try different encodings because some files might have encoding issues
    encodings = ['utf-8', 'latin-1', 'cp1252']
    last_error = None

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                lines = file.readlines()

                # Skip header row
                if lines:
                    lines = lines[1:]

                # Remove empty lines
                lines = [line.strip() for line in lines if line.strip()]

                return lines

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{filename}' not found. Please check the file path.")
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Unable to decode file '{filename}' with any of the attempted encodings: utf-8, latin-1, cp1252")
