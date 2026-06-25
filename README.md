# Personal Expense Tracker & Dashboard

A lightweight financial application featuring a unified Python terminal command-line interface paired with an interactive Streamlit visual web dashboard.

## Features
* **Hybrid Operations:** Log data through the fast terminal CLI backend tool or the graphical sidebar input fields.
* **Budget Tracking:** Enforce spending limits with automatic alerts when thresholds are breached.
* **Flexible Visualization:** Review financial histories through full yearly overviews or drill down into specific month-by-month filters.

## Project Structure
* `expense_tracker.py`: Core CLI script managing text-based asset logs and commands.
* `dashboard.py`: Interactive web graphics interface code engine.
* `expenses.json`: Local database engine tracking active records.
* `budget.json`: Configuration mapping storing monthly budget constraints.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Start the interactive frontend data visualization suite:
```bash
streamlit run dashboard.py
```
