"""
Unit tests for repository layer.
"""
import pytest
from unittest.mock import Mock
from src.repositories.base_repository import BaseRepository


class TestBaseRepository:
    """Test BaseRepository class."""
    
    def test_base_repository_initialization(self):
        """Test base repository initialization."""
        mock_db = Mock()
        mock_model = Mock()
        repository = BaseRepository(mock_db, mock_model)
        assert repository.model == mock_model
        assert repository.db == mock_db
    
    def test_base_repository_get_all(self):
        """Test get_all method."""
        mock_db = Mock()
        mock_model = Mock()
        mock_query = Mock()
        mock_query.all.return_value = [{'id': 1}, {'id': 2}]
        mock_db.query.return_value = mock_query
        
        repository = BaseRepository(mock_db, mock_model)
        repository.get_all()
        
        mock_db.query.assert_called_once_with(mock_model)
        mock_query.all.assert_called_once()
    
    def test_base_repository_get_by_id(self):
        """Test get_by_id method."""
        mock_db = Mock()
        mock_model = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = {'id': 1}
        mock_db.query.return_value = mock_query
        
        repository = BaseRepository(mock_db, mock_model)
        repository.get_by_id(1)
        
        mock_db.query.assert_called_once_with(mock_model)
    
    def test_base_repository_create(self):
        """Test create method."""
        mock_db = Mock()
        mock_model = Mock()
        mock_instance = Mock()
        mock_instance.id = 1
        mock_model.return_value = mock_instance
        
        repository = BaseRepository(mock_db, mock_model)
        repository.create(name='test')
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_base_repository_update(self):
        """Test update method."""
        mock_db = Mock()
        mock_model = Mock()
        mock_instance = Mock()
        mock_instance.id = 1
        
        repository = BaseRepository(mock_db, mock_model)
        repository.update(1, name='updated')
        
        mock_db.commit.assert_called_once()
    
    def test_base_repository_delete(self):
        """Test delete method."""
        mock_db = Mock()
        mock_model = Mock()
        mock_query = Mock()
        mock_instance = Mock()
        mock_query.filter.return_value.first.return_value = mock_instance
        mock_db.query.return_value = mock_query
        
        repository = BaseRepository(mock_db, mock_model)
        repository.delete(1)
        
        mock_db.delete.assert_called_once_with(mock_instance)
        mock_db.commit.assert_called_once()


class TestRepositoryIntegration:
    """Integration tests for repository layer."""
    
    def test_repository_model_integration(self):
        """Test repository and model integration."""
        mock_db = Mock()
        mock_model = Mock()
        repository = BaseRepository(mock_db, mock_model)
        
        assert repository.model == mock_model
        assert repository.db == mock_db
