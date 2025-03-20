import csv
import pandas as pd
import os

def reconcile_transactions(bank_file, ledger_file, report_path):
    """Reconciles transactions between bank and ledger based on debit/credit amounts."""
    bank_transactions = load_transactions(bank_file)
    ledger_transactions = load_transactions(ledger_file)

    reconciled = []
    unreconciled_bank = bank_transactions.copy()
    unreconciled_ledger = ledger_transactions.copy()

    matched_ledger_indices = set()

    for bank in bank_transactions:
        for idx, ledger in enumerate(ledger_transactions):
            if idx in matched_ledger_indices:
                continue  # Skip already matched transactions

            if bank["debit"] == ledger["credit"] or bank["credit"] == ledger["debit"]:
                reconciled.append({**bank, "status": "Reconciled"})
                matched_ledger_indices.add(idx)
                unreconciled_bank.remove(bank)
                break

    # Remove reconciled transactions from unreconciled_ledger
    unreconciled_ledger = [ledger for i, ledger in enumerate(ledger_transactions) if i not in matched_ledger_indices]

    # Combine all records into a DataFrame
    df = pd.DataFrame(reconciled + [{"status": "Unreconciled"} | t for t in unreconciled_bank + unreconciled_ledger])

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df.to_csv(report_path, index=False)

    return reconciled, unreconciled_bank, unreconciled_ledger

def load_transactions(file_path):
    """Loads transactions from a CSV file into a list of dictionaries."""
    transactions = []
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append({
                "date": row["Date"],
                "description": row["Description"],
                "debit": float(row.get("Debit", 0) or 0),
                "credit": float(row.get("Credit", 0) or 0),
                "balance": float(row.get("Balance", 0) or 0),
            })
    return transactions
