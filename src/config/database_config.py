"""
Database configuration management.
"""
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    def __init__(self, settings: Optional[object] = None):
        """
        Initialize database configuration.
        
        Args:
            settings: Settings object (optional, for future use)
        """
        # Direct environment variable access to avoid circular imports
        self.db_type = os.getenv('DB_TYPE', 'postgresql')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'dollar_prices')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
    
    @property
    def database_url(self) -> str:
        """Construct database URL from configuration."""
        if self.db_type == 'sqlite':
            return f"sqlite:///{self.db_name}"
        else:
            return (
                f"{self.db_type}://"
                f"{self.db_user}:{self.db_password}@"
                f"{self.db_host}:{self.db_port}/"
                f"{self.db_name}"
            )
    
    def create_engine(self, echo: bool = False):
        """Create SQLAlchemy engine."""
        return create_engine(self.database_url, echo=echo)
    
    def create_session_maker(self):
        """Create SQLAlchemy session maker."""
        engine = self.create_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_engine(self, echo: bool = False):
        """Get or create SQLAlchemy engine."""
        if not hasattr(self, '_engine'):
            self._engine = self.create_engine(echo)
        return self._engine
    
    def get_session_local(self):
        """Get or create session maker."""
        if not hasattr(self, '_session_local'):
            self._session_local = self.create_session_maker()
        return self._session_local
