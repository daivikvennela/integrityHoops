#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
Migrates all data from the local SQLite database to a PostgreSQL database.
"""

import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from urllib.parse import urlparse

def get_database_url():
    """Get PostgreSQL connection URL from environment or user input"""
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("\n🗄️  PostgreSQL Database Migration")
        print("=" * 50)
        print("\nPlease provide your PostgreSQL connection details:")
        
        host = input("Host (e.g., localhost or db.example.com): ")
        port = input("Port (default 5432): ") or "5432"
        database = input("Database name: ")
        user = input("Username: ")
        password = input("Password: ")
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Fix Heroku/Render postgres:// to postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def get_sqlite_path():
    """Get SQLite database path"""
    default_paths = [
        'basketball.db',
        'src/core/data/basketball.db',
        'data/basketball.db',
        '../basketball.db'
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    custom_path = input("\nSQLite database not found. Please enter path: ")
    if os.path.exists(custom_path):
        return custom_path
    
    print(f"❌ Error: File not found: {custom_path}")
    sys.exit(1)

def migrate_database():
    """Main migration function"""
    print("\n🚀 Starting Database Migration")
    print("=" * 50)
    
    # Get database connections
    sqlite_path = get_sqlite_path()
    print(f"\n✓ Found SQLite database: {sqlite_path}")
    
    db_url = get_database_url()
    print(f"✓ PostgreSQL connection configured")
    
    try:
        # Connect to SQLite
        print("\n📂 Connecting to SQLite...")
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        print("📂 Connecting to PostgreSQL...")
        pg_conn = psycopg2.connect(db_url)
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        pg_cursor = pg_conn.cursor()
        
        # Get all tables
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [table[0] for table in sqlite_cursor.fetchall()]
        
        if not tables:
            print("⚠️  No tables found in SQLite database")
            return
        
        print(f"\n📊 Found {len(tables)} tables to migrate:")
        for table in tables:
            print(f"   - {table}")
        
        # Migrate each table
        for table_name in tables:
            print(f"\n🔄 Migrating table: {table_name}")
            
            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = sqlite_cursor.fetchall()
            
            # Create table in PostgreSQL (drop if exists)
            print(f"   Creating table structure...")
            
            # Build CREATE TABLE statement
            column_defs = []
            for col in columns_info:
                col_name = col[1]
                col_type = col[2].upper()
                
                # Map SQLite types to PostgreSQL types
                if col_type in ('INTEGER', 'INT'):
                    pg_type = 'INTEGER'
                elif col_type in ('REAL', 'FLOAT', 'DOUBLE'):
                    pg_type = 'REAL'
                elif col_type == 'TEXT':
                    pg_type = 'TEXT'
                elif col_type == 'BLOB':
                    pg_type = 'BYTEA'
                else:
                    pg_type = 'TEXT'  # Default
                
                column_defs.append(f"{col_name} {pg_type}")
            
            # Drop and create table
            pg_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            create_statement = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
            pg_cursor.execute(create_statement)
            
            # Get all data
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"   ⚠️  No data to migrate")
                continue
            
            # Get column names
            columns = [col[1] for col in columns_info]
            
            # Insert data
            print(f"   Inserting {len(rows)} rows...")
            placeholders = ','.join(['%s'] * len(columns))
            insert_query = f"""
                INSERT INTO {table_name} ({','.join(columns)}) 
                VALUES ({placeholders})
            """
            
            success_count = 0
            error_count = 0
            
            for row in rows:
                try:
                    pg_cursor.execute(insert_query, row)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Only show first 5 errors
                        print(f"   ⚠️  Error inserting row: {e}")
            
            print(f"   ✓ Successfully migrated {success_count} rows")
            if error_count > 0:
                print(f"   ⚠️  {error_count} rows failed to migrate")
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Verify data in PostgreSQL")
        print("2. Update your application's DATABASE_URL")
        print("3. Test your application")
        print("4. Deploy to production\n")
        
    except sqlite3.Error as e:
        print(f"\n❌ SQLite Error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"\n❌ PostgreSQL Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        migrate_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(0)

