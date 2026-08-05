"""
Unit tests for database module.
"""
import pytest
from unittest.mock import Mock, patch
from src.database import DatabaseConfig, Database, db


class TestDatabaseConfig:
    """Test DatabaseConfig class."""
    
    def test_database_config_defaults(self):
        """Test default configuration values."""
        config = DatabaseConfig()
        
        assert config.db_host == 'localhost'
        assert config.db_port == '5432'
        assert config.db_name == 'dollar_prices'
        assert config.db_user == 'postgres'
        assert config.db_password == 'password'
    
    def test_database_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv('DB_HOST', 'testhost')
        monkeypatch.setenv('DB_PORT', '5433')
        monkeypatch.setenv('DB_NAME', 'testdb')
        monkeypatch.setenv('DB_USER', 'testuser')
        monkeypatch.setenv('DB_PASSWORD', 'testpass')
        
        config = DatabaseConfig()
        
        assert config.db_host == 'testhost'
        assert config.db_port == '5433'
        assert config.db_name == 'testdb'
        assert config.db_user == 'testuser'
        assert config.db_password == 'testpass'
    
    def test_database_url_construction(self):
        """Test database URL construction."""
        config = DatabaseConfig()
        url = config.database_url
        
        assert 'postgresql://' in url
        assert 'postgres:password' in url
        assert 'localhost:5432' in url
        assert 'dollar_prices' in url


class TestDatabase:
    """Test Database class."""
    
    @patch('src.database.create_engine')
    @patch('src.database.sessionmaker')
    def test_database_initialization(self, mock_sessionmaker, mock_create_engine):
        """Test Database initialization."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory
        
        database = Database('postgresql://test')
        
        mock_create_engine.assert_called_once_with('postgresql://test', echo=False)
        mock_sessionmaker.assert_called_once()
    
    @patch('src.database.create_engine')
    @patch('src.database.sessionmaker')
    def test_database_init_db(self, mock_sessionmaker, mock_create_engine):
        """Test database initialization."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory
        
        database = Database('postgresql://test')
        database.init_db()
        
        # Verify that create_tables was called
        # This would require mocking Base.metadata.create_all
    
    @patch('src.database.create_engine')
    @patch('src.database.sessionmaker')
    def test_get_session(self, mock_sessionmaker, mock_create_engine):
        """Test getting a database session."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session = Mock()
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        database = Database('postgresql://test')
        session = database.get_session()
        
        mock_session_factory.assert_called_once()
        assert session == mock_session