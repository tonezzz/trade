"""
Database connection and configuration.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models import Base
from src.config.database_config import DatabaseConfig


class Database:
    """Database connection manager."""
    
    def __init__(self, database_url: str = None, config: DatabaseConfig = None):
        """
        Initialize database connection.
        
        Args:
            database_url: Optional database URL. If not provided, uses configuration.
            config: Optional DatabaseConfig instance.
        """
        if database_url is None:
            if config is None:
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
