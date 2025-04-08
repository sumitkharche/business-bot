import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('fieldedge_new.db') # Using a new filename to avoid conflicts
    cursor = conn.cursor()

    # --- Drop existing tables if they exist (optional, useful for rerunning) ---
    cursor.execute("DROP TABLE IF EXISTS Invoices")
    cursor.execute("DROP TABLE IF EXISTS WorkOrders")
    cursor.execute("DROP TABLE IF EXISTS Quotes")
    cursor.execute("DROP TABLE IF EXISTS Technicians")
    cursor.execute("DROP TABLE IF EXISTS Customers")
    print("Existing tables dropped (if any).")

    # --- Tables Creation (Using your new definitions) ---
    print("Creating new tables...")
    cursor.execute('''
        CREATE TABLE Customers (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT, -- Use AUTOINCREMENT for easier ID generation
            Name TEXT,
            Email TEXT,
            Phone TEXT,
            City TEXT,
            CreatedDate TEXT -- Store dates as TEXT in ISO format (YYYY-MM-DD)
        )
    ''')
    cursor.execute('''
        CREATE TABLE Technicians (
            TechnicianID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Specialization TEXT,
            ExperienceYears INTEGER,
            HireDate TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE Quotes (
            QuoteID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID INTEGER,
            Amount REAL, -- Use REAL for floating-point numbers
            Status TEXT,  -- e.g., 'Accepted', 'Rejected', 'Missed', 'Sent'
            CreatedDate TEXT,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE WorkOrders (
            WorkOrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID INTEGER,
            TechnicianID INTEGER,
            Status TEXT,
            CreatedDate TEXT,
            CompletionDate TEXT, -- Can be NULL if not completed
            TravelTimeMinutes INTEGER,
            WorkHours REAL,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
            FOREIGN KEY (TechnicianID) REFERENCES Technicians(TechnicianID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE Invoices (
            InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
            WorkOrderID INTEGER,
            Amount REAL,
            IssuedDate TEXT,
            FOREIGN KEY (WorkOrderID) REFERENCES WorkOrders(WorkOrderID)
        )
    ''')
    print("Tables created successfully.")

    # --- Dummy Data Insertion ---
    print("Generating and inserting dummy data...")

    # Settings
    num_customers = 100
    num_technicians = 15
    num_work_orders = 250
    num_quotes = 300
    start_date_customers = datetime(2021, 1, 1)
    start_date_technicians = datetime(2020, 1, 1)
    start_date_activities = datetime(2022, 1, 1)
    end_date_activities = datetime.now() # Use current date as end point
    date_range_days = (end_date_activities - start_date_activities).days

    # 1. Generate Customers
    customers_data = []
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
    for i in range(num_customers):
        name = f"Customer {i+1}"
        email = f"customer{i+1}@example.com"
        phone = f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
        city = random.choice(cities)
        created_date = start_date_customers + timedelta(days=random.randint(0, (end_date_activities - start_date_customers).days))
        customers_data.append((name, email, phone, city, created_date.strftime('%Y-%m-%d')))
    cursor.executemany("INSERT INTO Customers (Name, Email, Phone, City, CreatedDate) VALUES (?, ?, ?, ?, ?)", customers_data)
    print(f"{num_customers} customers inserted.")

      # 2. Generate Technicians
    technicians_data = []
    specializations = ['HVAC', 'Plumbing', 'Electrical', 'Appliance Repair', 'General Maintenance']
    for i in range(num_technicians):
        name = f"Technician {i+1}"
        specialization = random.choice(specializations)
        experience = random.randint(1, 25) # Years of experience

        # --- CORRECTED HIRE DATE LOGIC ---
        # Estimate experience duration (using 365.25 to account for leap years)
        experience_duration = timedelta(days=int(365.25 * experience))

        # Calculate the latest *possible* hire date to have 'experience' years by 'end_date_activities'
        latest_possible_hire_date = end_date_activities - experience_duration

        # The absolute earliest hire date is 'start_date_technicians'
        earliest_hire_date = start_date_technicians

        # Determine the effective latest date for the random range.
        # It cannot be earlier than the earliest possible date.
        effective_latest_hire_date = max(earliest_hire_date, latest_possible_hire_date)

        # Calculate the number of days in the valid hiring period
        hiring_period_days = (effective_latest_hire_date - earliest_hire_date).days

        # Ensure the range isn't negative (it shouldn't be with max(), but safety first)
        if hiring_period_days < 0:
            hiring_period_days = 0 # Default to hiring on earliest date if calculation fails

        # Select a random day within the allowed period
        random_days_offset = random.randint(0, hiring_period_days)

        # Calculate the final hire date
        hire_date = earliest_hire_date + timedelta(days=random_days_offset)
        # --- END OF CORRECTED LOGIC ---

        technicians_data.append((name, specialization, experience, hire_date.strftime('%Y-%m-%d')))

    cursor.executemany("INSERT INTO Technicians (Name, Specialization, ExperienceYears, HireDate) VALUES (?, ?, ?, ?)", technicians_data)
    print(f"{num_technicians} technicians inserted.")

    # 3. Generate Work Orders (and potentially related Invoices)
    work_orders_data = []
    invoices_data = []
    wo_statuses = ['Scheduled', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
    generated_wo_ids = [] # Keep track of generated IDs for invoices

    for i in range(num_work_orders):
        customer_id = random.randint(1, num_customers)
        technician_id = random.randint(1, num_technicians)
        status = random.choice(wo_statuses)
        created_date = start_date_activities + timedelta(days=random.randint(0, date_range_days))
        completion_date = None
        work_hours = None
        invoice_amount = None

        if status == 'Completed':
            completion_delta = random.randint(0, 14) # Completed within 0-14 days
            completion_date_dt = created_date + timedelta(days=completion_delta)
            # Ensure completion date is not in the future if created_date is very recent
            if completion_date_dt > end_date_activities:
                completion_date_dt = end_date_activities
            completion_date = completion_date_dt.strftime('%Y-%m-%d')
            work_hours = round(random.uniform(0.5, 8.0), 1)
            # Generate an invoice for completed work orders
            invoice_amount = round(random.uniform(50.0, 1500.0), 2)
            issued_date_dt = completion_date_dt + timedelta(days=random.randint(0, 5))
            if issued_date_dt > end_date_activities:
                issued_date_dt = end_date_activities
            issued_date = issued_date_dt.strftime('%Y-%m-%d')
            # We'll add to invoices_data *after* getting the WorkOrderID

        elif status in ['In Progress', 'Scheduled']:
             work_hours = round(random.uniform(0.0, 4.0), 1) # Might have some hours logged

        travel_time = random.randint(15, 120) # Travel time in minutes

        work_orders_data.append((
            customer_id, technician_id, status,
            created_date.strftime('%Y-%m-%d'), completion_date,
            travel_time, work_hours
        ))

        # Insert the Work Order and get its ID
        cursor.execute('''
            INSERT INTO WorkOrders (CustomerID, TechnicianID, Status, CreatedDate, CompletionDate, TravelTimeMinutes, WorkHours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', work_orders_data[-1]) # Insert the last added tuple
        work_order_id = cursor.lastrowid # Get the auto-generated ID
        generated_wo_ids.append(work_order_id)

        # Now create the invoice if applicable, using the retrieved work_order_id
        if invoice_amount is not None:
            invoices_data.append((work_order_id, invoice_amount, issued_date))

    print(f"{num_work_orders} work orders inserted.")

    # 4. Bulk Insert Invoices (created during WO loop)
    if invoices_data:
        cursor.executemany("INSERT INTO Invoices (WorkOrderID, Amount, IssuedDate) VALUES (?, ?, ?)", invoices_data)
        print(f"{len(invoices_data)} invoices inserted.")

    # 5. Generate Quotes
    quotes_data = []
    quote_statuses = ['Sent', 'Accepted', 'Rejected', 'Missed']
    for i in range(num_quotes):
        customer_id = random.randint(1, num_customers)
        amount = round(random.uniform(100.0, 5000.0), 2)
        status = random.choice(quote_statuses)
        created_date = start_date_activities + timedelta(days=random.randint(0, date_range_days))
        # Ensure quote date isn't after today
        if created_date > end_date_activities:
            created_date = end_date_activities

        quotes_data.append((customer_id, amount, status, created_date.strftime('%Y-%m-%d')))

    cursor.executemany("INSERT INTO Quotes (CustomerID, Amount, Status, CreatedDate) VALUES (?, ?, ?, ?)", quotes_data)
    print(f"{num_quotes} quotes inserted.")

    # --- Commit Changes and Close Connection ---
    conn.commit()
    conn.close()
    print("Database 'fieldedge_new.db' created and populated successfully.")

# Run the function
if __name__ == "__main__":
    create_database()