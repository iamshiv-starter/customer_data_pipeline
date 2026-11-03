import csv
import sqlite3

connection = sqlite3.connect("transactions.db")
print("Database created and Successfully Connected to SQLite")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        customer_id TEXT,
        amount REAL,
        transaction_date TEXT
    )
""")
print("Transaction tasble created successfully")


with open('data/transactions.csv', 'r') as file:
    reader = csv.DictReader(file)

    transaction_id_valid = set()
    valid_transaction = []
    invalid_transaction =[ ]

    for row in reader:
        transaction_id = row["transaction_id"]
        amount = row["amount"]
        
        if transaction_id in transaction_id_valid:
           # print("Invalid transaction: Duplicate id", transaction_id) 
            invalid_transaction.append(row)
        elif amount == '':
            invalid_transaction.append(row)
            #print(transaction_id, "Invalid tranaction: Missing amount")
        elif float(amount) < 0:
           # print(transaction_id, "Invalid Transaction: Negative amount")
            invalid_transaction.append(row)
        else:
            #print(transaction_id, "valid amount", amount)
            transaction_id_valid.add(transaction_id)
            valid_transaction.append(row)
    for transactions in valid_transaction:
        transaction_id = transactions['transaction_id']
        customer_id = transactions['customer_id']
        amount = float(transactions['amount'])
        transaction_date = transactions['transaction_date']

        cursor.execute("""INSERT OR IGNORE INTO transactions (
        transaction_id,
        customer_id,
        amount,
        transaction_date)
        VALUES (?, ?, ?, ?)""", (transaction_id, customer_id, amount, transaction_date))
# print(transaction_id, customer_id, amount, transaction_date)
# print("Ready to load", len(valid_transaction), "transactions")

for transactions in valid_transaction:
 print(transactions)
connection.commit()
print("Transactions loaded into datase")

cursor.execute("Select * from transactions")
results = cursor.fetchall()

for transaction in results:
    print(transaction)

print("Valid transactions:", len(valid_transaction))
print("Invalid transactions:", len(invalid_transaction))
print("Total transactions:", len(valid_transaction) + len(invalid_transaction))
connection.close()
