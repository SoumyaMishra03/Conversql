import pandas as pd

# Load the master CSV file
df = pd.read_csv(r"C:\Users\NITRO\OneDrive\Desktop\Datasets\bank_transactions.csv")

# --- 1. Create the Customers table ---
# Select customer-specific columns (without dropping duplicates)
customers = df[
    ["CustomerID", "CustomerDOB", "CustGender", "CustLocation", "CustAccountBalance"]
]
customers.to_csv("customers.csv", index=False)

# --- 2. Create the Transactions table ---
# Select transaction-specific columns (retain CustomerID to relate to the Customers table)
transactions = df[
    ["TransactionID", "CustomerID", "TransactionDate", "TransactionTime", "TransactionAmount (INR)"]
]
transactions.to_csv("transactions.csv", index=False)

print("Created customers.csv and transactions.csv successfully.")