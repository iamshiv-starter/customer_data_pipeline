
# Import the CSV library to read transaction data from a CSV file
import csv

# Import SQLite to create and interact with a local SQL database
import sqlite3


# ============================================================
# STEP 1: DATABASE CONNECTION AND TABLE CREATION
# ============================================================

# Connect to the SQLite database.
# If transactions.db does not exist, SQLite creates it.
connection = sqlite3.connect("transactions.db")

print("Successfully connected to SQLite database")

# Create a cursor to execute SQL queries
cursor = connection.cursor()

# Create the transactions table if it does not already exist.
# PRIMARY KEY ensures that transaction IDs are unique.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        customer_id TEXT,
        amount REAL,
        transaction_date TEXT
    )
""")

print("Transactions table created successfully")


# ============================================================
# STEP 2: EXTRACT - READ DATA FROM CSV
# ============================================================

# Open the CSV file in read mode.
# The with statement automatically closes the file afterward.
with open('data/transactions.csv', 'r') as file:

    # DictReader converts each CSV row into a Python dictionary.
    # Column names become dictionary keys.
    reader = csv.DictReader(file)

    # Store IDs of valid transactions to detect duplicates.
    transaction_id_valid = set()

    # Store complete transaction records based on validation.
    valid_transaction = []
    invalid_transaction = []


    # ========================================================
    # STEP 3: TRANSFORM - DATA QUALITY VALIDATION
    # ========================================================

    # Loop through every transaction in the CSV file.
    for row in reader:

        # Extract transaction ID and amount from the current row.
        transaction_id = row["transaction_id"]
        amount = row["amount"]

        # Check 1: Reject duplicate transaction IDs.
        if transaction_id in transaction_id_valid:
            invalid_transaction.append(row)

        # Check 2: Reject transactions with missing amounts.
        elif amount == '':
            invalid_transaction.append(row)

        # Check 3: Reject transactions with negative amounts.
        elif float(amount) < 0:
            invalid_transaction.append(row)

        # If all checks pass, the transaction is valid.
        else:

            # Add the ID to the set for future duplicate checks.
            transaction_id_valid.add(transaction_id)

            # Store the complete valid transaction dictionary.
            valid_transaction.append(row)


# ============================================================
# STEP 4: LOAD - INSERT VALID TRANSACTIONS INTO SQLITE
# ============================================================

# Loop through only the transactions that passed validation.
for transactions in valid_transaction:

    # Extract individual values from each transaction dictionary.
    transaction_id = transactions['transaction_id']
    customer_id = transactions['customer_id']

    # Convert the amount from a string to a floating-point number.
    amount = float(transactions['amount'])

    transaction_date = transactions['transaction_date']

    # Insert the valid transaction into the SQLite table.
    # Question marks (?) are placeholders for Python values.
    # INSERT OR IGNORE skips rows that violate constraints,
    # such as an existing transaction_id primary key.
    cursor.execute("""
        INSERT OR IGNORE INTO transactions (
            transaction_id,
            customer_id,
            amount,
            transaction_date
        )
        VALUES (?, ?, ?, ?)
    """, (transaction_id, customer_id, amount, transaction_date))


# ============================================================
# STEP 5: COMMIT - SAVE DATABASE CHANGES
# ============================================================

# Commit the transaction inserts to save them permanently.
connection.commit()

print("Transaction loading completed")


# ============================================================
# STEP 6: VERIFY - RETRIEVE DATA FROM SQLITE
# ============================================================

# Retrieve all records currently stored in the transactions table.
cursor.execute("SELECT * FROM transactions")

# Fetch all query results as a list of tuples.
results = cursor.fetchall()

# Print each transaction retrieved from the database.
for transaction in results:
    print(transaction)


# ============================================================
# STEP 7: DATA QUALITY MONITORING
# ============================================================

# Display how many CSV records passed and failed validation.
print("Valid transactions:", len(valid_transaction))
print("Invalid transactions:", len(invalid_transaction))

# Calculate the total number of CSV records processed.
print("Total transactions:", len(valid_transaction) + len(invalid_transaction))


# ============================================================
# STEP 8: CLOSE DATABASE CONNECTION
# ============================================================

# Close the SQLite connection after all operations are complete.
connection.close()
