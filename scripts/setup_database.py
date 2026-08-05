#!/usr/bin/env python3
"""
Database Setup Wizard
Automated database initialization and configuration wizard.
"""
import os
import sys
import getpass
from pathlib import Path
from typing import Optional, Tuple
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Base


class DatabaseSetupWizard:
    """Interactive database setup wizard."""
    
    def __init__(self):
        self.env_file = Path('.env')
        self.config = {}
        
    def welcome(self):
        """Display welcome message."""
        print("=" * 60)
        print("Dollar Price Database - Setup Wizard")
        print("=" * 60)
        print("This wizard will help you configure and initialize the database.")
        print()
        
    def choose_database_type(self) -> str:
        """Prompt user to choose database type."""
        print("Choose database type:")
        print("1. PostgreSQL (recommended for production)")
        print("2. SQLite (simple, file-based, good for development)")
        print()
        
        while True:
            choice = input("Enter choice [1-2]: ").strip()
            if choice == '1':
                return 'postgresql'
            elif choice == '2':
                return 'sqlite'
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def configure_postgresql(self) -> dict:
        """Configure PostgreSQL connection parameters."""
        print("\n--- PostgreSQL Configuration ---")
        config = {}
        
        config['db_host'] = input("PostgreSQL host [localhost]: ").strip() or 'localhost'
        config['db_port'] = input("PostgreSQL port [5432]: ").strip() or '5432'
        config['db_name'] = input("Database name [dollar_prices]: ").strip() or 'dollar_prices'
        config['db_user'] = input("PostgreSQL user [postgres]: ").strip() or 'postgres'
        config['db_password'] = getpass.getpass("PostgreSQL password: ")
        
        return config
    
    def configure_sqlite(self) -> dict:
        """Configure SQLite database."""
        print("\n--- SQLite Configuration ---")
        config = {}
        
        default_db = 'dollar_prices.db'
        config['db_name'] = input(f"Database file name [{default_db}]: ").strip() or default_db
        
        return config
    
    def test_connection(self, db_type: str, config: dict) -> Tuple[bool, Optional[str]]:
        """Test database connection."""
        print("\nTesting database connection...")
        
        try:
            if db_type == 'postgresql':
                url = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/postgres"
                engine = create_engine(url, connect_args={'connect_timeout': 5})
                
                with engine.connect() as conn:
                    # Test connection to postgres database first
                    conn.execute(text("SELECT 1"))
                
                # Check if target database exists
                url_target = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
                engine_target = create_engine(url_target, connect_args={'connect_timeout': 5})
                
                try:
                    with engine_target.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    print("✓ Database exists and connection successful")
                    return True, None
                except sqlalchemy.exc.OperationalError:
                    print("✓ Connection successful, database will be created")
                    return True, None
                    
            else:  # SQLite
                url = f"sqlite:///{config['db_name']}"
                engine = create_engine(url)
                
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                print("✓ SQLite database connection successful")
                return True, None
                
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
    
    def create_database(self, db_type: str, config: dict) -> Tuple[bool, Optional[str]]:
        """Create database if it doesn't exist."""
        if db_type == 'sqlite':
            # SQLite creates database automatically on first connection
            return True, None
        
        print(f"\nCreating database '{config['db_name']}' if it doesn't exist...")
        
        try:
            # Connect to postgres database to create new database
            url = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/postgres"
            engine = create_engine(url, connect_args={'connect_timeout': 5})
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :dbname"
                ), {'dbname': config['db_name']})
                
                if result.fetchone():
                    print(f"✓ Database '{config['db_name']}' already exists")
                    return True, None
                
                # Create database
                conn.execute(text("COMMIT"))  # Commit any transaction
                conn.execute(text(f"CREATE DATABASE {config['db_name']}"))
                conn.execute(text("COMMIT"))
                
            print(f"✓ Database '{config['db_name']}' created successfully")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to create database: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
    
    def create_schema(self, db_type: str, config: dict) -> Tuple[bool, Optional[str]]:
        """Create database schema/tables."""
        print("\nCreating database schema...")
        
        try:
            if db_type == 'postgresql':
                url = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
            else:
                url = f"sqlite:///{config['db_name']}"
            
            engine = create_engine(url)
            Base.metadata.create_all(bind=engine)
            
            print("✓ Database schema created successfully")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to create schema: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
    
    def save_env_file(self, db_type: str, config: dict):
        """Save configuration to .env file."""
        print("\nSaving configuration to .env file...")
        
        env_content = f"# Database Configuration\n"
        
        if db_type == 'postgresql':
            env_content += f"DB_TYPE=postgresql\n"
            env_content += f"DB_HOST={config['db_host']}\n"
            env_content += f"DB_PORT={config['db_port']}\n"
            env_content += f"DB_NAME={config['db_name']}\n"
            env_content += f"DB_USER={config['db_user']}\n"
            env_content += f"DB_PASSWORD={config['db_password']}\n"
        else:
            env_content += f"DB_TYPE=sqlite\n"
            env_content += f"DB_NAME={config['db_name']}\n"
        
        # Add notification configuration placeholders
        env_content += f"\n# Notification Configuration\n"
        env_content += f"NOTIFICATIONS_ENABLED=false\n"
        env_content += f"NOTIFICATION_EMAIL=your_email@example.com\n"
        env_content += f"SMTP_SERVER=smtp.gmail.com\n"
        env_content += f"SMTP_PORT=587\n"
        env_content += f"SMTP_USERNAME=your_smtp_username\n"
        env_content += f"SMTP_PASSWORD=your_smtp_password\n"
        env_content += f"SMTP_FROM_EMAIL=your_email@example.com\n"
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            print(f"✓ Configuration saved to {self.env_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to save .env file: {str(e)}")
            return False
    
    def verify_setup(self, db_type: str, config: dict) -> Tuple[bool, Optional[str]]:
        """Verify the complete setup."""
        print("\nVerifying setup...")
        
        try:
            # Reload environment variables
            load_dotenv()
            
            if db_type == 'postgresql':
                url = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
            else:
                url = f"sqlite:///{config['db_name']}"
            
            engine = create_engine(url)
            
            # Check if tables exist
            with engine.connect() as conn:
                inspector = sqlalchemy.inspect(engine)
                tables = inspector.get_table_names()
                
                expected_tables = [
                    'exchange_rates', 'dollar_index', 'commodity_prices',
                    'signal_history', 'signal_performance', 'backtest_results', 'backtest_trades'
                ]
                
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if missing_tables:
                    return False, f"Missing tables: {', '.join(missing_tables)}"
                
                print(f"✓ All {len(expected_tables)} tables verified")
            
            return True, None
            
        except Exception as e:
            return False, f"Verification failed: {str(e)}"
    
    def run(self):
        """Run the complete setup wizard."""
        self.welcome()
        
        # Step 1: Choose database type
        db_type = self.choose_database_type()
        
        # Step 2: Configure database
        if db_type == 'postgresql':
            config = self.configure_postgresql()
        else:
            config = self.configure_sqlite()
        
        # Step 3: Test connection
        success, error = self.test_connection(db_type, config)
        if not success:
            print(f"\n✗ Setup failed: {error}")
            print("Please check your configuration and try again.")
            return False
        
        # Step 4: Create database
        success, error = self.create_database(db_type, config)
        if not success:
            print(f"\n✗ Setup failed: {error}")
            return False
        
        # Step 5: Create schema
        success, error = self.create_schema(db_type, config)
        if not success:
            print(f"\n✗ Setup failed: {error}")
            return False
        
        # Step 6: Save configuration
        if not self.save_env_file(db_type, config):
            print("\n⚠ Warning: Failed to save .env file, but database was created successfully.")
        
        # Step 7: Verify setup
        success, error = self.verify_setup(db_type, config)
        if not success:
            print(f"\n⚠ Warning: {error}")
        
        # Success message
        print("\n" + "=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)
        print(f"\nDatabase type: {db_type}")
        if db_type == 'postgresql':
            print(f"Host: {config['db_host']}:{config['db_port']}")
            print(f"Database: {config['db_name']}")
        else:
            print(f"Database file: {config['db_name']}")
        
        print("\nNext steps:")
        print("1. Download historical data: python3 download_data.py")
        print("2. Import data: python3 cli.py import <data_type> <file_path>")
        print("3. Query data: python3 cli.py query <data_type>")
        print("4. Start API server: python3 scripts/run_api.py")
        
        return True


def main():
    """Main entry point."""
    wizard = DatabaseSetupWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()