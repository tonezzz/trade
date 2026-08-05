"""
Database connection and configuration.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from src.models import Base

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'postgresql')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'dollar_prices')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
    
    @property
    def database_url(self):
        """Construct database URL from configuration."""
        if self.db_type == 'sqlite':
            return f"sqlite:///{self.db_name}"
        else:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class Database:
    """Database connection manager."""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database connection.
        
        Args:
            database_url: Optional database URL. If not provided, uses environment variables.
        """
        if database_url is None:
            config = DatabaseConfig()
            database_url = config.database_url
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def init_db(self):
        """Initialize database with all tables."""
        self.create_tables()
        print("Database tables created successfully.")


# Global database instance
db = Database()


def get_db():
    """Dependency for getting database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
