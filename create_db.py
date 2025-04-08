import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    conn = sqlite3.connect('fieldedge.db')
    cursor = conn.cursor()

    # Tables Creation (same as before)
    cursor.execute('''
        CREATE TABLE Customers (
            CustomerID INTEGER PRIMARY KEY,
            Name TEXT,
            Address TEXT,
            Phone TEXT,
            Value REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE WorkOrders (
            WorkOrderID INTEGER PRIMARY KEY,
            CustomerID INTEGER,
            TechnicianID INTEGER,
            Date TEXT,
            Description TEXT,
            Status TEXT,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
            FOREIGN KEY (TechnicianID) REFERENCES Technicians(TechnicianID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE Invoices (
            InvoiceID INTEGER PRIMARY KEY,
            WorkOrderID INTEGER,
            Amount REAL,
            Date TEXT,
            FOREIGN KEY (WorkOrderID) REFERENCES WorkOrders(WorkOrderID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE Quotes (
            QuoteID INTEGER PRIMARY KEY,
            CustomerID INTEGER,
            Amount REAL,
            Date TEXT,
            Status TEXT,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE Technicians (
            TechnicianID INTEGER PRIMARY KEY,
            Name TEXT,
            PerformanceScore REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE YearlyRevenue (
            Year INTEGER PRIMARY KEY,
            Revenue REAL
        )
    ''')

    # Dummy Data Insertion (expanded and related)
    customers = []
    for _ in range(100):
        customers.append((f"Customer{_}", f"{random.randint(100, 999)} Random St", f"555-{random.randint(1000, 9999)}", random.uniform(2000, 10000)))
    cursor.executemany("INSERT INTO Customers (Name, Address, Phone, Value) VALUES (?, ?, ?, ?)", customers)

    technicians = []
    for _ in range(10):
        technicians.append((f"Technician{_}", random.uniform(70, 100)))
    cursor.executemany("INSERT INTO Technicians (Name, PerformanceScore) VALUES (?, ?)", technicians)

    start_date = datetime(2022, 1, 1)
    work_orders = []
    invoices = []
    quotes = []

    for _ in range(200):
        customer_id = random.randint(1, 100)
        technician_id = random.randint(1, 10)
        date = start_date + timedelta(days=random.randint(0, 730))
        description = random.choice(["AC Repair", "Furnace Install", "Duct Cleaning", "Maintenance"])
        status = random.choice(["Completed", "Pending", "Scheduled"])

        work_orders.append((customer_id, technician_id, date.strftime('%Y-%m-%d'), description, status))

        invoice_amount = random.uniform(50, 1000)
        invoices.append((_ + 1, invoice_amount, date.strftime('%Y-%m-%d')))

        quote_amount = random.uniform(100, 1500)
        quote_status = random.choice(["Sent", "Accepted", "Rejected"])
        quotes.append((customer_id, quote_amount, date.strftime('%Y-%m-%d'), quote_status))

    cursor.executemany("INSERT INTO WorkOrders (CustomerID, TechnicianID, Date, Description, Status) VALUES (?, ?, ?, ?, ?)", work_orders)
    cursor.executemany("INSERT INTO Invoices (WorkOrderID, Amount, Date) VALUES (?, ?, ?)", invoices)
    cursor.executemany("INSERT INTO Quotes (CustomerID, Amount, Date, Status) VALUES (?, ?, ?, ?)", quotes)

    for year in range(2020, 2024):
        revenue = random.uniform(40000, 80000)
        cursor.execute("INSERT INTO YearlyRevenue (Year, Revenue) VALUES (?, ?)", (year, revenue))

    conn.commit()
    conn.close()

create_database()