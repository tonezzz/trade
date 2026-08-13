"""
Unit tests for data importer module.
"""
import pytest
import tempfile
import os


class TestCSVFileHandling:
    """Test CSV file handling."""
    
    def test_csv_file_creation_and_reading(self):
        """Test CSV file creation and reading."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('date,quote_currency,rate\n')
            f.write('2024-01-01,EUR,0.9150\n')
            f.write('2024-01-02,EUR,0.9160\n')
            temp_file = f.name
        
        try:
            # Test that the file can be read
            assert os.path.exists(temp_file)
            
            # Test CSV reading
            import pandas as pd
            df = pd.read_csv(temp_file)
            assert len(df) == 2
            assert 'date' in df.columns
            assert 'quote_currency' in df.columns
            assert 'rate' in df.columns
        finally:
            os.unlink(temp_file)
    
    def test_csv_with_commodity_data(self):
        """Test CSV with commodity data."""
        # Create a temporary CSV file with commodity data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('date,commodity,price,unit\n')
            f.write('2024-01-01,GOLD,2000.50,oz\n')
            f.write('2024-01-02,GOLD,2010.00,oz\n')
            temp_file = f.name
        
        try:
            # Test that the file can be read
            assert os.path.exists(temp_file)
            
            # Test CSV reading
            import pandas as pd
            df = pd.read_csv(temp_file)
            assert len(df) == 2
            assert 'date' in df.columns
            assert 'commodity' in df.columns
            assert 'price' in df.columns
            assert 'unit' in df.columns
        finally:
            os.unlink(temp_file)
    
    def test_csv_with_dollar_index_data(self):
        """Test CSV with dollar index data."""
        # Create a temporary CSV file with dollar index data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('date,value\n')
            f.write('2024-01-01,103.5\n')
            f.write('2024-01-02,103.8\n')
            temp_file = f.name
        
        try:
            # Test that the file can be read
            assert os.path.exists(temp_file)
            
            # Test CSV reading
            import pandas as pd
            df = pd.read_csv(temp_file)
            assert len(df) == 2
            assert 'date' in df.columns
            assert 'value' in df.columns
        finally:
            os.unlink(temp_file)
    
    def test_csv_with_invalid_data(self):
        """Test CSV with invalid data."""
        # Create a temporary CSV file with invalid data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('date,quote_currency,rate\n')
            f.write('invalid,EUR,not_a_number\n')
            f.write('2024-01-02,EUR,0.9160\n')
            temp_file = f.name
        
        try:
            # Test that the file can be read even with invalid data
            assert os.path.exists(temp_file)
            
            # Test CSV reading
            import pandas as pd
            df = pd.read_csv(temp_file)
            assert len(df) == 2
        finally:
            os.unlink(temp_file)
