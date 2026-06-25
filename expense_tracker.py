import argparse
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

# Helper: Load data from JSON file
def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# Helper: Save data to JSON file
def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

# Feature: Add Expense
def add_expense(description, amount):
    expenses = load_expenses()
    next_id = max([e["id"] for e in expenses], default=0) + 1
    
    new_expense = {
        "id": next_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount)
    }
    expenses.append(new_expense)
    save_expenses(expenses)
    print(f"# Expense added successfully (ID: {next_id})")

# Feature: List Expenses
def list_expenses():
    expenses = load_expenses()
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'# ID':<5} {'Date':<12} {'Description':<20} {'Amount'}")
    for e in expenses:
        print(f"# {e['id']:<3} {e['date']:<12} {e['description']:<20} ${e['amount']:.2f}")

# Feature: Delete Expense
def delete_expense(expense_id):
    expenses = load_expenses()
    updated_expenses = [e for e in expenses if e["id"] != expense_id]
    
    if len(expenses) == len(updated_expenses):
        print(f"Error: Expense with ID {expense_id} not found.")
    else:
        save_expenses(updated_expenses)
        print("# Expense deleted successfully")

# Feature: Summary & Month Filtering
def show_summary(month=None):
    expenses = load_expenses()
    current_year = datetime.now().year
    
    if month:
        # Filter expenses matching the specified month and current year
        filtered = [
            e for e in expenses 
            if datetime.strptime(e["date"], "%Y-%m-%d").month == month 
            and datetime.strptime(e["date"], "%Y-%m-%d").year == current_year
        ]
        month_name = datetime(current_year, month, 1).strftime("%B")
        total = sum(e["amount"] for e in filtered)
        print(f"# Total expenses for {month_name}: ${total:.2f}")
    else:
        total = sum(e["amount"] for e in expenses)
        print(f"# Total expenses: ${total:.2f}")

# Main Argument Parser Configurations
def main():
    parser = argparse.ArgumentParser(description="Expense Tracker CLI Application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--description", required=True, help="Description of the expense")
    add_parser.add_argument("--amount", type=float, required=True, help="Amount spent")

    # Command: list
    subparsers.add_parser("list", help="List all recorded expenses")

    # Command: delete
    delete_parser = subparsers.add_parser("delete", help="Delete an expense by ID")
    delete_parser.add_argument("--id", type=int, required=True, help="ID of the expense to remove")

    # Command: summary
    summary_parser = subparsers.add_parser("summary", help="Show total expense summary")
    summary_parser.add_argument("--month", type=int, choices=range(1, 13), help="Filter summary by month (1-12)")

    args = parser.parse_args()

    # Route arguments to correct functions
    if args.command == "add":
        add_expense(args.description, args.amount)
    elif args.command == "list":
        list_expenses()
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "summary":
        show_summary(month=args.month)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
