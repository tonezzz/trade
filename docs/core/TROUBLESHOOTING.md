
---

**Last Updated: 2026-08-04
# Dollar Price Database - Troubleshooting Guide

This guide provides solutions to common issues encountered when setting up, running, and maintaining the Dollar Price Database system.

## Table of Contents

1. [Database Connection Issues](#database-connection-issues)
2. [Import Failures and Solutions](#import-failures-and-solutions)
3. [API Errors and Fixes](#api-errors-and-fixes)
4. [Performance Problems](#performance-problems)
5. [Data Quality Issues](#data-quality-issues)
6. [Automation Issues](#automation-issues)
7. [Visualization Problems](#visualization-problems)
8. [Environment and Setup Issues](#environment-and-setup-issues)
9. [FAQ with Solutions](#faq-with-solutions)

## Database Connection Issues

### Issue: "Connection refused" or "Could not connect to server"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Causes**:
- PostgreSQL is not running
- Wrong host or port in configuration
- Firewall blocking connection
- PostgreSQL not listening on expected interface

**Solutions**:

1. **Check if PostgreSQL is running**:
```bash
# Linux/Mac
sudo service postgresql status
# or
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo service postgresql start
# or
sudo systemctl start postgresql
```

2. **Verify PostgreSQL is listening**:
```bash
# Check if PostgreSQL is listening on port 5432
sudo netstat -tlnp | grep 5432
# or
sudo lsof -i :5432
```

3. **Check PostgreSQL configuration**:
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf

# Ensure these lines are uncommented:
listen_addresses = 'localhost'  # or '*' for all interfaces
port = 5432
```

4. **Check pg_hba.conf for authentication**:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Ensure proper authentication method (e.g., md5 or scram-sha-256)
# Example line:
# local   all             postgres                                md5
# host    all             all             127.0.0.1/32            md5
```

5. **Restart PostgreSQL after configuration changes**:
```bash
sudo service postgresql restart
# or
sudo systemctl restart postgresql
```

### Issue: "FATAL: database does not exist"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: FATAL: database "dollar_prices" does not exist
```

**Causes**:
- Database not created
- Wrong database name in configuration

**Solutions**:

1. **Create the database**:
```bash
# Using createdb
createdb dollar_prices

# Or using psql
psql -U postgres
CREATE DATABASE dollar_prices;
\q
```

2. **Verify database exists**:
```bash
psql -U postgres -l
# Look for dollar_prices in the list
```

3. **Check .env configuration**:
```bash
cat .env | grep DB_NAME
# Ensure it matches the created database name
```

### Issue: "FATAL: password authentication failed"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: FATAL: password authentication failed for user "postgres"
```

**Causes**:
- Wrong password in .env file
- PostgreSQL user password changed
- Authentication method mismatch

**Solutions**:

1. **Reset PostgreSQL user password**:
```bash
# Switch to postgres user
sudo -u postgres psql

# Reset password
ALTER USER postgres WITH PASSWORD 'your_new_password';
\q
```

2. **Update .env file**:
```bash
nano .env
# Update DB_PASSWORD with the correct password
```

3. **Test connection manually**:
```bash
psql -U postgres -d dollar_prices -h localhost
# Enter password when prompted
```

### Issue: "FATAL: role does not exist"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: FATAL: role "db_user" does not exist
```

**Causes**:
- Database user not created
- Wrong username in configuration

**Solutions**:

1. **Create the database user**:
```bash
sudo -u postgres psql

CREATE USER dollar_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE dollar_prices TO dollar_user;
\q
```

2. **Update .env file**:
```bash
nano .env
# Update DB_USER and DB_PASSWORD
```

### Issue: "SSL connection required"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: server closed the connection unexpectedly
```

**Causes**:
- PostgreSQL requires SSL but client doesn't support it
- SSL configuration mismatch

**Solutions**:

1. **Disable SSL requirement in PostgreSQL**:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Change sslmode from require to prefer or disable
# hostssl all all 127.0.0.1/32 md5
# to
# host all all 127.0.0.1/32 md5
```

2. **Add SSL parameter to connection string**:
```bash
# In .env or database.py
DATABASE_URL=postgresql://user:pass@localhost:5432/db?sslmode=disable
```

## Import Failures and Solutions

### Issue: "File not found" error during import

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/imported/file.csv'
```

**Causes**:
- Wrong file path
- File not downloaded yet
- File in wrong directory

**Solutions**:

1. **Check file location**:
```bash
ls -la data/imported/
ls -la data/archive/
```

2. **Download data first**:
```bash
python3 download_data.py
```

3. **Use absolute path**:
```bash
python cli.py import commodity_prices /full/path/to/file.csv
```

4. **Check file permissions**:
```bash
chmod 644 data/imported/file.csv
```

### Issue: "Invalid CSV format" error

**Symptoms**:
```
ValueError: Invalid CSV format - missing required columns
```

**Causes**:
- CSV doesn't match template format
- Missing required columns
- Wrong column names
- Incorrect date format

**Solutions**:

1. **Compare with template**:
```bash
# Check template
head -5 data/templates/commodity_prices_template.csv

# Check your file
head -5 your_file.csv
```

2. **Validate column names**:
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
print(df.columns.tolist())
```

3. **Check date format**:
```python
# Dates should be YYYY-MM-DD
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
print(df[df['date'].isna()])
```

4. **Reformat CSV**:
```python
import pandas as pd

# Read CSV
df = pd.read_csv('raw_data.csv')

# Rename columns to match template
df = df.rename(columns={
    'Date': 'date',
    'Price': 'price',
    # Add other mappings as needed
})

# Save in correct format
df.to_csv('formatted_data.csv', index=False)
```

### Issue: "Duplicate entry" error during import

**Symptoms**:
```
IntegrityError: duplicate key value violates unique constraint
```

**Causes**:
- Data already exists in database
- Same date + currency/symbol combination
- Importing same file twice

**Solutions**:

1. **Check existing data**:
```bash
python cli.py query commodity_prices --commodity GOLD
```

2. **Use upsert instead of insert** (if supported):
```python
# Modify importer.py to use ON CONFLICT
# This requires database schema changes
```

3. **Filter out existing dates before import**:
```python
import pandas as pd
from src.database import db
from src.models import CommodityPrice

# Get existing dates
existing_dates = db.session.query(CommodityPrice.date).filter(
    CommodityPrice.commodity == 'GOLD'
).all()
existing_dates = {d[0] for d in existing_dates}

# Filter new data
df = pd.read_csv('new_data.csv')
df = df[~df['date'].isin(existing_dates)]

# Import filtered data
df.to_csv('filtered_data.csv', index=False)
```

4. **Clear existing data and reimport**:
```bash
# Be careful with this - it deletes data!
python -c "from src.database import db; from src.models import CommodityPrice; db.session.query(CommodityPrice).filter(CommodityPrice.commodity == 'GOLD').delete(); db.session.commit()"
```

### Issue: "Data validation failed" error

**Symptoms**:
```
ValidationError: Data validation failed: price cannot be negative
```

**Causes**:
- Invalid data values (negative prices, invalid dates)
- Data type mismatches
- Missing required fields

**Solutions**:

1. **Validate data before import**:
```python
import pandas as pd

df = pd.read_csv('data.csv')

# Check for negative prices
print(df[df['price'] < 0])

# Check for missing values
print(df.isnull().sum())

# Check date range
print(df['date'].min(), df['date'].max())
```

2. **Clean invalid data**:
```python
# Remove negative prices
df = df[df['price'] >= 0]

# Fill missing values
df['volume'] = df['volume'].fillna(0)

# Remove rows with missing required fields
df = df.dropna(subset=['date', 'price'])
```

3. **Skip validation (not recommended)**:
```bash
# In config/data_sources.yml
settings:
  skip_validation: true
```

### Issue: "Memory error" during large import

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Causes**:
- Importing very large CSV files
- Insufficient system memory
- Loading entire file into memory

**Solutions**:

1. **Import in chunks**:
```python
import pandas as pd
from src.importer import import_commodity_prices

chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    import_commodity_prices(chunk)
```

2. **Use streaming import**:
```python
import csv
from src.importer import import_commodity_prices

with open('large_file.csv', 'r') as f:
    reader = csv.DictReader(f)
    batch = []
    for i, row in enumerate(reader):
        batch.append(row)
        if len(batch) >= 1000:
            import_commodity_prices(batch)
            batch = []
    # Import remaining
    if batch:
        import_commodity_prices(batch)
```

3. **Increase system memory**:
```bash
# Close other applications
# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## API Errors and Fixes

### Issue: "404 Not Found" on API endpoints

**Symptoms**:
```
HTTPException: 404 Not Found
```

**Causes**:
- Wrong endpoint URL
- Resource doesn't exist
- Case sensitivity in URLs

**Solutions**:

1. **Check API documentation**:
```bash
# Visit http://localhost:8000/docs
# Review available endpoints
```

2. **Verify endpoint URL**:
```bash
# Correct
curl http://localhost:8000/api/exchange_rates/EUR

# Wrong (case sensitive)
curl http://localhost:8000/api/exchange_rates/eur
```

3. **Check if data exists**:
```bash
python cli.py query exchange_rates --currency EUR
```

### Issue: "422 Unprocessable Entity" validation error

**Symptoms**:
```
HTTPException: 422 Unprocessable Entity
```

**Causes**:
- Invalid request parameters
- Wrong data types
- Missing required fields

**Solutions**:

1. **Check API documentation for expected parameters**:
```bash
# Visit /docs for parameter details
```

2. **Validate request format**:
```bash
# Example: Check date format
curl "http://localhost:8000/api/exchange_rates/EUR?start_date=2024-01-01&end_date=2024-12-31"
```

3. **Use correct data types**:
```python
# Wrong
{"limit": "100"}  # String instead of int

# Correct
{"limit": 100}  # Integer
```

### Issue: "500 Internal Server Error"

**Symptoms**:
```
HTTPException: 500 Internal Server Error
```

**Causes**:
- Database connection issues
- Application errors
- Unhandled exceptions

**Solutions**:

1. **Check server logs**:
```bash
# Check terminal where FastAPI is running
# Or check logs directory
tail -f logs/automation.log
```

2. **Check database connection**:
```bash
python -c "from src.database import db; print('Connection OK')"
```

3. **Test endpoint directly**:
```python
from src.queries import get_queries
queries = get_queries()
df = queries.get_exchange_rates('EUR')
print(df.head())
```

4. **Enable debug mode**:
```python
# In api.py, temporarily add:
app = FastAPI(debug=True)
```

### Issue: CORS errors in browser

**Symptoms**:
```
Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Causes**:
- CORS not configured properly
- Browser security policy

**Solutions**:

1. **Check CORS middleware configuration**:
```python
# In api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **For development, allow all origins**:
```python
allow_origins=["*"]  # Not recommended for production
```

3. **Use proxy in development**:
```javascript
// In frontend development
// Configure proxy to avoid CORS
```

## Performance Problems

### Issue: Slow query performance

**Symptoms**:
- Queries taking > 10 seconds
- API timeouts
- CLI commands hanging

**Causes**:
- Missing database indexes
- Large dataset queries
- Inefficient query patterns

**Solutions**:

1. **Check query execution plan**:
```sql
EXPLAIN ANALYZE
SELECT * FROM exchange_rates 
WHERE quote_currency = 'EUR' 
AND date BETWEEN '2020-01-01' AND '2024-12-31';
```

2. **Add missing indexes**:
```sql
-- Check existing indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'exchange_rates';

-- Add index if missing
CREATE INDEX idx_exchange_date_currency 
ON exchange_rates(date, quote_currency);
```

3. **Use date ranges in queries**:
```python
# Bad - queries all data
df = queries.get_exchange_rates('EUR')

# Good - limits data
df = queries.get_exchange_rates('EUR', start_date='2024-01-01', end_date='2024-12-31')
```

4. **Optimize pagination**:
```python
# Use limit and offset
df = queries.get_exchange_rates('EUR', limit=1000, offset=0)
```

### Issue: High memory usage

**Symptoms**:
- System running out of memory
- Application crashes
- Slow performance

**Causes**:
- Loading large datasets into memory
- Memory leaks
- Inefficient data processing

**Solutions**:

1. **Process data in chunks**:
```python
chunk_size = 10000
for chunk in pd.read_sql(query, db.engine, chunksize=chunk_size):
    process_chunk(chunk)
```

2. **Use generators instead of lists**:
```python
# Bad - loads all into memory
results = [item for item in large_dataset]

# Good - generator
results = (item for item in large_dataset)
```

3. **Close database connections**:
```python
# Ensure sessions are closed
from src.database import db
session = db.Session()
try:
    # operations
    pass
finally:
    session.close()
```

4. **Monitor memory usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")
```

### Issue: Database connection pool exhaustion

**Symptoms**:
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Causes**:
- Too many connections
- Connections not being released
- Pool size too small

**Solutions**:

1. **Increase connection pool size**:
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from default 5
    max_overflow=40,  # Increase from default 10
    pool_timeout=30
)
```

2. **Ensure sessions are closed**:
```python
# Use context manager
with db.session() as session:
    # operations
    pass
# Session automatically closed
```

3. **Use connection pooling properly**:
```python
# Don't create new engines for each request
# Reuse existing engine
```

## Data Quality Issues

### Issue: Missing data in time series

**Symptoms**:
- Gaps in date sequences
- Missing weekends/holidays
- Inconsistent data frequency

**Causes**:
- Data source doesn't provide continuous data
- Import errors
- Data source outages

**Solutions**:

1. **Identify missing dates**:
```python
import pandas as pd

df = queries.get_exchange_rates('EUR')
df['date'] = pd.to_datetime(df['date'])

# Create complete date range
date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')

# Find missing dates
missing_dates = date_range.difference(df['date'])
print(f"Missing dates: {len(missing_dates)}")
```

2. **Forward-fill missing data**:
```python
df = df.set_index('date')
df = df.asfreq('D').fillna(method='ffill')
```

3. **Use last available price for gaps**:
```python
df['rate'] = df['rate'].fillna(method='ffill')
```

4. **Document data source limitations**:
```python
# Some sources don't provide weekend data
# This is expected behavior
```

### Issue: Outliers in price data

**Symptoms**:
- Extreme price spikes
- Impossible values
- Data quality issues

**Causes**:
- Data entry errors
- Market anomalies
- Currency/unit confusion

**Solutions**:

1. **Identify outliers**:
```python
import pandas as pd

df = queries.get_exchange_rates('EUR')

# Statistical method
mean = df['rate'].mean()
std = df['rate'].std()
outliers = df[(df['rate'] - mean).abs() > 3 * std]
print(outliers)
```

2. **Visual inspection**:
```python
import matplotlib.pyplot as plt
df['rate'].plot()
plt.show()
```

3. **Validate against reasonable ranges**:
```python
# EUR/USD should be between 0.5 and 2.0
df = df[(df['rate'] > 0.5) & (df['rate'] < 2.0)]
```

4. **Cross-reference with other sources**:
```python
# Compare with alternative data source
# Flag discrepancies for manual review
```

### Issue: Inconsistent data formats

**Symptoms**:
- Mixed date formats
- Different number formats
- Encoding issues

**Causes**:
- Multiple data sources
- Manual data entry
- Format changes over time

**Solutions**:

1. **Standardize date formats**:
```python
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
```

2. **Normalize number formats**:
```python
# Remove commas, currency symbols
df['price'] = df['price'].str.replace(',', '').str.replace('$', '').astype(float)
```

3. **Handle encoding issues**:
```python
# Specify encoding when reading CSV
df = pd.read_csv('file.csv', encoding='utf-8')
# or
df = pd.read_csv('file.csv', encoding='latin-1')
```

## Automation Issues

### Issue: Scheduler not running jobs

**Symptoms**:
- Jobs not executing on schedule
- No error messages
- Scheduler appears stuck

**Causes**:
- Scheduler process not running
- Configuration errors
- Time zone issues

**Solutions**:

1. **Check scheduler status**:
```bash
python scripts/auto_update.py --status
```

2. **Run manually to test**:
```bash
python scripts/auto_update.py --run-once --dry-run
```

3. **Check configuration syntax**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/data_sources.yml'))"
```

4. **Check time zone settings**:
```python
import datetime
print(f"Local time: {datetime.datetime.now()}")
print(f"UTC time: {datetime.datetime.utcnow()}")
```

### Issue: Jobs failing consistently

**Symptoms**:
- Jobs retrying multiple times
- Error notifications
- No data being imported

**Causes**:
- Data source unavailable
- Network issues
- Authentication problems

**Solutions**:

1. **Check job logs**:
```bash
tail -f logs/automation.log
```

2. **Test data source manually**:
```bash
curl -I https://example.com/data.csv
```

3. **Increase retry count**:
```yaml
# In config/data_sources.yml
settings:
  max_retries: 5
  retry_delay: 10
```

4. **Check network connectivity**:
```bash
ping example.com
traceroute example.com
```

### Issue: Email notifications not sending

**Symptoms**:
- No error notifications received
- SMTP errors in logs

**Causes**:
- SMTP configuration errors
- Authentication issues
- Firewall blocking SMTP

**Solutions**:

1. **Test SMTP configuration**:
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test email")
msg['Subject'] = 'Test'
msg['From'] = 'your_email@example.com'
msg['To'] = 'recipient@example.com'

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('username', 'password')
    server.send_message(msg)
```

2. **Check .env configuration**:
```bash
cat .env | grep SMTP
```

3. **Use app-specific password for Gmail**:
- Generate app-specific password in Google Account settings
- Use instead of regular password

4. **Check firewall settings**:
```bash
sudo ufw allow 587/tcp
```

## Visualization Problems

### Issue: Charts not displaying correctly

**Symptoms**:
- Blank charts
- Missing data
- Incorrect styling

**Causes**:
- Data format issues
- Plotly version conflicts
- Browser compatibility

**Solutions**:

1. **Check data before charting**:
```python
df = queries.get_exchange_rates('EUR')
print(df.head())
print(df.info())
```

2. **Test simple chart first**:
```python
import plotly.express as px
fig = px.line(df, x='date', y='rate')
fig.show()
```

3. **Check Plotly version**:
```bash
pip show plotly
# Update if needed
pip install --upgrade plotly
```

4. **Export to HTML and open in browser**:
```python
fig.write_html('test_chart.html')
# Open test_chart.html in browser
```

### Issue: Chart export fails

**Symptoms**:
```
ValueError: Error while saving plot
```

**Causes**:
- Invalid file path
- Permission issues
- Missing kaleido package for static export

**Solutions**:

1. **Check file path**:
```python
import os
print(os.path.exists('/path/to/output'))
```

2. **Create directory if needed**:
```bash
mkdir -p charts/
```

3. **Install kaleido for static export**:
```bash
pip install kaleido
```

4. **Check file permissions**:
```bash
chmod 755 charts/
```

## Environment and Setup Issues

### Issue: Python module not found

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
```

**Causes**:
- Not in virtual environment
- PYTHONPATH not set
- Module not installed

**Solutions**:

1. **Activate virtual environment**:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set PYTHONPATH**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# or
python -m src.module
```

4. **Install in development mode**:
```bash
pip install -e .
```

### Issue: Permission denied errors

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Causes**:
- File permissions
- Directory ownership
- Running as wrong user

**Solutions**:

1. **Check file permissions**:
```bash
ls -la file.py
```

2. **Fix permissions**:
```bash
chmod 644 file.py
chmod 755 directory/
```

3. **Change ownership if needed**:
```bash
sudo chown -R $USER:$USER /path/to/project
```

4. **Run with appropriate permissions**:
```bash
# Don't use sudo unless necessary
# Fix permissions instead
```

## FAQ with Solutions

### Q: How do I reset the database completely?

**A**: Use these commands with caution - this deletes all data:

```bash
# Drop database
psql -U postgres -c "DROP DATABASE dollar_prices;"

# Recreate database
psql -U postgres -c "CREATE DATABASE dollar_prices;"

# Reinitialize schema
python -c "from src.database import db; db.init_db()"
```

### Q: How do I back up the database?

**A**: Use pg_dump for backups:

```bash
# Full backup
pg_dump -U postgres dollar_prices > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres dollar_prices | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
psql -U postgres dollar_prices < backup_20240101.sql
# or
gunzip < backup_20240101.sql.gz | psql -U postgres dollar_prices
```

### Q: How do I add a new data source?

**A**: Follow these steps:

1. **Add to config/data_sources.yml**:
```yaml
new_source:
  name: "New Data Source"
  type: "commodity"
  url: "https://example.com/data.csv"
  schedule: "daily"
  schedule_time: "06:00"
  import_function: "import_commodity_prices"
  enabled: true
```

2. **Create formatter function if needed**:
```python
def format_new_source_data(raw_file, formatted_file):
    # Format data to match template
    pass
```

3. **Test with dry run**:
```bash
python scripts/auto_update.py --run-once --job new_source --dry-run
```

### Q: How do I monitor system health?

**A**: Use the health check endpoint:

```bash
curl http://localhost:8000/api/health
```

Or use the CLI:
```bash
python scripts/auto_update.py --status
```

### Q: How do I update to the latest version?

**A**: Follow these steps:

```bash
# Backup database first
pg_dump -U postgres dollar_prices > backup_before_update.sql

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations if needed
python -c "from src.database import db; db.upgrade()"

# Test system
python cli.py query exchange_rates --currency EUR
```

### Q: How do I improve query performance for large datasets?

**A**: Use these strategies:

1. **Add appropriate indexes**
2. **Use date range filters**
3. **Implement pagination**
4. **Consider read replicas**
5. **Use materialized views for complex queries**

### Q: How do I handle timezone issues?

**A**: Standardize on UTC:

```python
from datetime import datetime, timezone

# Always use UTC
now = datetime.now(timezone.utc)

# Convert for display
local_time = now.astimezone()
```

### Q: How do I debug import issues?

**A**: Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or check logs
tail -f logs/automation.log
```

### Q: How do I set up the system for production?

**A**: Follow production checklist:

1. **Use strong passwords**
2. **Enable SSL/TLS**
3. **Configure firewall**
4. **Set up monitoring**
5. **Configure backups**
6. **Use environment variables**
7. **Disable debug mode**
8. **Implement rate limiting**
9. **Set up log rotation**
10. **Configure CORS properly**

### Q: How do I contribute to the project?

**A**: Follow contribution guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## Getting Additional Help

If you encounter issues not covered in this guide:

1. **Check existing documentation**:
   - README.md
   - ARCHITECTURE.md
   - API_GUIDE.md
   - docs/ directory

2. **Review logs**:
   - logs/automation.log
   - Application logs
   - Database logs

3. **Search issue tracker**:
   - GitHub issues
   - Stack Overflow

4. **Ask for help**:
   - Create a GitHub issue with:
     - Error messages
     - Steps to reproduce
     - System information
     - Logs (sanitized)

## Prevention and Best Practices

### Regular Maintenance

1. **Monitor disk space**:
```bash
df -h
```

2. **Check database size**:
```sql
SELECT pg_size_pretty(pg_database_size('dollar_prices'));
```

3. **Review logs regularly**:
```bash
tail -100 logs/automation.log
```

4. **Test backups**:
```bash
# Restore backup to test database
```

### Monitoring Setup

1. **Set up alerts for**:
   - Disk space > 80%
   - Database connection failures
   - Job failures
   - API errors

2. **Regular health checks**:
```bash
# Add to cron
0 * * * * /path/to/health_check.sh
```

3. **Performance monitoring**:
- Query performance
- API response times
- Resource utilization

This troubleshooting guide should help resolve most common issues. For complex problems, provide detailed error messages and system information when seeking help.