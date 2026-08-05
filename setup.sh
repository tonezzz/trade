#!/bin/bash
# Setup script for Dollar Price Database

echo "Setting up Dollar Price Database..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your database credentials"
fi

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "Warning: PostgreSQL client not found. Please ensure PostgreSQL is installed."
else
    echo "PostgreSQL client found."
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database credentials"
echo "2. Create the database: createdb dollar_prices"
echo "3. Initialize the database: python cli.py init"
echo "4. Import data: python cli.py import exchange_rates data/templates/exchange_rates_template.csv"
echo ""
echo "For more information, see README.md"
