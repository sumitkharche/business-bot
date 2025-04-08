import pandas as pd
from db_config import engine # Assuming db_config.py sets up your SQLAlchemy engine

def format_optional(value, prefix="", suffix="", default="N/A"):
    """Helper function to format values that might be None or missing."""
    if pd.isna(value) or value is None:
        return default
    return f"{prefix}{value}{suffix}"

def extract_customers():
    """Extracts customer data (no joins needed)."""
    try:
        df = pd.read_sql("SELECT * FROM Customers ORDER BY CustomerID", engine)
        return [
            f"Customer {row['CustomerID']}: Name: {row['Name']}, Email: {row['Email']}, Phone: {row['Phone']}, City: {row['City']}, Created: {row['CreatedDate']}"
            for _, row in df.iterrows()
        ]
    except Exception as e:
        print(f"Error extracting customers: {e}")
        return []

def extract_technicians():
    """Extracts technician data (no joins needed)."""
    try:
        df = pd.read_sql("SELECT * FROM Technicians ORDER BY TechnicianID", engine)
        return [
            f"Technician {row['TechnicianID']}: Name: {row['Name']}, Specialization: {row['Specialization']}, Experience: {row['ExperienceYears']} years, Hired: {row['HireDate']}"
            for _, row in df.iterrows()
        ]
    except Exception as e:
        print(f"Error extracting technicians: {e}")
        return []

def extract_quotes_with_customer():
    """Extracts quotes linked to customer names."""
    sql = """
    SELECT
        q.QuoteID, q.Amount, q.Status, q.CreatedDate,
        c.CustomerID, c.Name as CustomerName
    FROM Quotes q
    LEFT JOIN Customers c ON q.CustomerID = c.CustomerID
    ORDER BY q.QuoteID;
    """
    try:
        df = pd.read_sql(sql, engine)
        return [
            f"Quote {row['QuoteID']}: Customer: '{row['CustomerName']}' (ID: {row['CustomerID']}), Amount: {row['Amount']:.2f}, Status: {row['Status']}, Created: {row['CreatedDate']}"
            for _, row in df.iterrows()
        ]
    except Exception as e:
        print(f"Error extracting quotes: {e}")
        return []

def extract_workorders_detailed():
    """Extracts work orders linked to customer and technician names, including more details."""
    sql = """
    SELECT
        wo.WorkOrderID, wo.Status, wo.CreatedDate, wo.CompletionDate,
        wo.TravelTimeMinutes, wo.WorkHours,
        c.CustomerID, c.Name as CustomerName,
        t.TechnicianID, t.Name as TechnicianName
    FROM WorkOrders wo
    LEFT JOIN Customers c ON wo.CustomerID = c.CustomerID
    LEFT JOIN Technicians t ON wo.TechnicianID = t.TechnicianID
    ORDER BY wo.WorkOrderID;
    """
    try:
        df = pd.read_sql(sql, engine)
        results = []
        for _, row in df.iterrows():
            # Format optional fields nicely
            completion_str = format_optional(row['CompletionDate'], prefix="Completed: ")
            travel_str = format_optional(row['TravelTimeMinutes'], prefix="Travel: ", suffix=" mins")
            hours_str = format_optional(row['WorkHours'], prefix="Hours: ")

            results.append(
                f"WorkOrder {row['WorkOrderID']}: "
                f"Customer: '{row['CustomerName']}' (ID: {row['CustomerID']}), "
                f"Technician: '{row['TechnicianName']}' (ID: {row['TechnicianID']}), "
                f"Status: {row['Status']}, Created: {row['CreatedDate']}, "
                f"{completion_str}, {travel_str}, {hours_str}"
            )
        return results
    except Exception as e:
        print(f"Error extracting work orders: {e}")
        return []


def extract_invoices_detailed():
    """Extracts invoices linked to work orders and customers."""
    sql = """
    SELECT
        i.InvoiceID, i.Amount, i.IssuedDate,
        wo.WorkOrderID, wo.CreatedDate as WOCreatedDate,
        c.CustomerID, c.Name as CustomerName
    FROM Invoices i
    LEFT JOIN WorkOrders wo ON i.WorkOrderID = wo.WorkOrderID
    LEFT JOIN Customers c ON wo.CustomerID = c.CustomerID
    ORDER BY i.InvoiceID;
    """
    try:
        df = pd.read_sql(sql, engine)
        return [
            (f"Invoice {row['InvoiceID']}: "
            f"WorkOrder: {row['WorkOrderID']} (for Customer '{row['CustomerName']}' [ID:{row['CustomerID']}] created on {row['WOCreatedDate']}), "
            f"Amount: {row['Amount']:.2f}, Issued: {row['IssuedDate']}")
            for _, row in df.iterrows()
        ]
    except Exception as e:
        print(f"Error extracting invoices: {e}")
        return []

def get_all_chunks():
    """Combines chunks from all tables, using JOINs for better context."""
    print("Extracting data with joins...")
    chunks = (
        extract_customers()
        + extract_technicians()
        + extract_quotes_with_customer()
        + extract_workorders_detailed()
        + extract_invoices_detailed()
    )
    print(f"Total chunks extracted: {len(chunks)}")
    return chunks

# --- Example Usage (assuming db_config.py exists and engine is valid) ---
# if __name__ == "__main__":
#     # Make sure your db_config.py defines the 'engine' variable
#     # Example db_config.py:
#     # from sqlalchemy import create_engine
#     # DATABASE_URL = "sqlite:///fieldedge_new.db" # Or your actual DB connection string
#     # engine = create_engine(DATABASE_URL)
#
#     all_data = get_all_linked_chunks()
#     if all_data:
#         print("\n--- Sample Chunks ---")
#         for chunk in all_data[:5]: # Print first 5 chunks as sample
#             print(chunk)
#         print("...")
#         for chunk in all_data[-5:]: # Print last 5 chunks as sample
#             print(chunk)
#     else:
#         print("No data extracted.")
#