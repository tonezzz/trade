#!/usr/bin/env python3
"""
Script to create trade database and move tables from chaba.
"""
import sys
import os
import psycopg2
from psycopg2 import sql

def create_trade_database():
    """Create the trade database."""
    try:
        # Connect to postgres database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='chaba',
            password='',  # Try without password first
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database
        cursor.execute('CREATE DATABASE trade')
        print("✅ Database 'trade' created successfully")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        if 'password' in str(e):
            print("❌ Database requires password. Please update the script with your PostgreSQL password.")
            print("Add your password to the connection string: password='your_password'")
            return False
        else:
            print(f"❌ Error creating database: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def migrate_tables():
    """Move tables from chaba to trade database."""
    try:
        # Connect to chaba database
        conn = chaba_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='chaba',
            password='',
            database='chaba'
        )
        chaba_conn.autocommit = True
        chaba_cursor = chaba_conn.cursor()
        
        # Connect to trade database
        trade_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='chaba',
            password='',
            database='trade'
        )
        trade_conn.autocommit = True
        trade_cursor = trade_conn.cursor()
        
        print("🔄 Moving tables from chaba to trade...")
        
        # Move each table
        tables = ['exchange_rates', 'dollar_index', 'commodity_prices']
        
        for table in tables:
            print(f"  Moving {table}...")
            
            # Get table definition from chaba
            chaba_cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            columns = chaba_cursor.fetchall()
            
            # Create table in trade
            column_defs = []
            for col in columns:
                col_name, data_type, is_nullable, col_default = col
                nullable = 'NOT NULL' if is_nullable == 'NO' else ''
                default = f"DEFAULT {col_default}" if col_default else ''
                column_defs.append(f"{col_name} {data_type} {nullable} {default}")
            
            create_sql = f"""
                CREATE TABLE {table} (
                    {', '.join(column_defs)}
                )
            """
            trade_cursor.execute(create_sql)
            
            # Copy data
            trade_cursor.execute(f"INSERT INTO {table} SELECT * FROM chaba.public.{table}")
            
            # Create indexes
            if table == 'exchange_rates':
                trade_cursor.execute('CREATE INDEX idx_exchange_date_currency ON exchange_rates (date, quote_currency)')
                trade_cursor.execute('CREATE INDEX idx_exchange_currency_date ON exchange_rates (quote_currency, date)')
            elif table == 'dollar_index':
                trade_cursor.execute('CREATE INDEX idx_dollar_index_date ON dollar_index (date)')
            elif table == 'commodity_prices':
                trade_cursor.execute('CREATE INDEX idx_commodity_date_symbol ON commodity_prices (date, symbol)')
                trade_cursor.execute('CREATE INDEX idx_commodity_symbol_date ON commodity_prices (symbol, date)')
            
            print(f"  ✅ {table} moved successfully")
        
        trade_conn.close()
        chaba_conn.close()
        
        print("✅ All tables migrated to trade database successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating tables: {e}")
        return False


def update_env_file():
    """Update .env file to use trade database."""
    try:
        env_path = '.env'
        
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update DB_NAME to trade
        updated_lines = []
        for line in lines:
            if line.startswith('DB_NAME='):
                updated_lines.append('DB_NAME=trade\n')
            else:
                updated_lines.append(line)
        
        # Write updated .env
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated to use trade database")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def main():
    """Main migration process."""
    print("=" * 60)
    print("DATABASE MIGRATION: chaba → trade")
    print("=" * 60)
    print()
    
    # Step 1: Create trade database
    print("Step 1: Creating trade database...")
    if not create_trade_database():
        print("\n❌ Migration failed at database creation step.")
        print("Please ensure PostgreSQL is running and you have the correct permissions.")
        sys.exit(1)
    
    print()
    
    # Step 2: Migrate tables
    print("Step 2: Migrating tables...")
    if not migrate_tables():
        print("\n❌ Migration failed at table migration step.")
        sys.exit(1)
    
    print()
    
    # Step 3: Update .env
    print("Step 3: Updating .env configuration...")
    if not update_env_file():
        print("\n❌ Migration failed at .env update step.")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ MIGRATION COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Reinitialize the database schema:")
    print("   python -c \"from src.database import db; db.init_db()\"")
    print("2. Test the connection:")
    print("   python cli.py health")
    print("3. Your application will now use the trade database")
    print()


if __name__ == '__main__':
    main()
