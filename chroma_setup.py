from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import sqlite3

def load_data_into_chroma():
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

    conn = sqlite3.connect('fieldedge.db')
    cursor = conn.cursor()

    # Load data from all tables
    tables = ['Customers', 'WorkOrders', 'Invoices', 'Quotes', 'Technicians', 'YearlyRevenue']
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            db.add_texts([str(row)], metadatas=[{"source": table, "row": str(row)}])

    conn.close()
    return db

chroma_db = load_data_into_chroma()