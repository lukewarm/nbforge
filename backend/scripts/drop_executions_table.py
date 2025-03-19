import os
import sys
from pathlib import Path

# Add the parent directory to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()

def drop_executions_table():
    """Drop the executions table to allow it to be recreated with updated schema"""
    print("Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Dropping executions table...")
    with engine.connect() as conn:
        # Drop the table with CASCADE to handle any dependencies
        conn.execute(text("DROP TABLE IF EXISTS executions CASCADE"))
        conn.commit()
    
    print("Executions table dropped successfully.")
    print("The table will be recreated with the updated schema on next application start.")

if __name__ == "__main__":
    # Confirm with the user before proceeding
    user_input = input("This will drop the executions table and all its data. Are you sure? (y/n): ")
    if user_input.lower() == 'y':
        drop_executions_table()
    else:
        print("Operation cancelled.") 