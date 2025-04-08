from sqlalchemy import create_engine

DB_PATH = "sqlite:///fieldedge_new.db"  # Make sure your .db file is in same directory
engine = create_engine(DB_PATH)