#!/usr/bin/env python3
"""
Thai Gold Price Downloader using GoldAPI.io
Downloads XAU/THB gold prices with efficient caching to respect API limits (100 calls/month)

Modes:
- latest: Fetch only the latest price (default)
- historical: Fetch historical data for a date range
- test: Test API connectivity with minimal calls
"""
import os
import json
import requests
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOLD_API_KEY = os.getenv('GOLD_API_KEY')
API_BASE_URL = "https://www.goldapi.io/api/XAU/THB"
HISTORICAL_URL_PATTERN = "https://www.goldapi.io/api/XAU/THB/{date}"
FALLBACK_API = "https://api.chnwt.dev/thai-gold-api/latest"

# Cache configuration
CACHE_DIR = Path("data/cache")
CACHE_FILE = CACHE_DIR / "thai_gold_cache.json"
HISTORICAL_CACHE_FILE = CACHE_DIR / "thai_gold_historical.json"
USAGE_FILE = CACHE_DIR / "goldapi_usage.json"
IMPORT_DIR = Path("data/imported")
MAX_CALLS_PER_MONTH = 100
CACHE_DURATION_HOURS = 24

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
IMPORT_DIR.mkdir(parents=True, exist_ok=True)


def is_weekday():
    """Check if today is a weekday (Thai gold markets closed weekends)."""
    return datetime.now().weekday() < 5  # 0-4 are Monday-Friday


def load_cache():
    """Load cached Thai gold data."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None


def save_cache(data):
    """Save data to cache with timestamp."""
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)


def is_cache_fresh():
    """Check if cached data is still fresh (within 24 hours)."""
    cache = load_cache()
    if not cache:
        return False
    
    cache_time = datetime.fromisoformat(cache['timestamp'])
    age = datetime.now() - cache_time
    return age < timedelta(hours=CACHE_DURATION_HOURS)


def load_usage_tracking():
    """Load API usage tracking data."""
    if USAGE_FILE.exists():
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
    return {'calls': [], 'monthly_count': 0, 'month': datetime.now().strftime('%Y-%m')}


def save_usage_tracking(usage_data):
    """Save API usage tracking data."""
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage_data, f, indent=2)


def check_rate_limit():
    """Check if we're within the monthly API call limit."""
    usage = load_usage_tracking()
    current_month = datetime.now().strftime('%Y-%m')
    
    # Reset monthly count if we're in a new month
    if usage['month'] != current_month:
        usage['month'] = current_month
        usage['monthly_count'] = 0
        usage['calls'] = []
    
    return usage['monthly_count'] < MAX_CALLS_PER_MONTH, usage


def record_api_call(endpoint, success=True):
    """Record an API call for usage tracking."""
    usage = load_usage_tracking()
    current_month = datetime.now().strftime('%Y-%m')
    
    # Reset monthly count if we're in a new month
    if usage['month'] != current_month:
        usage['month'] = current_month
        usage['monthly_count'] = 0
        usage['calls'] = []
    
    # Record the call
    call_record = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'success': success
    }
    usage['calls'].append(call_record)
    usage['monthly_count'] = len(usage['calls'])
    
    save_usage_tracking(usage)
    return usage


def fetch_from_goldapi(date_str=None):
    """Fetch Thai gold price from GoldAPI.io.
    
    Args:
        date_str: Optional date string in YYYYMMDD format for historical data.
                  If None, fetches latest price.
    """
    if not GOLD_API_KEY:
        print("❌ GOLD_API_KEY not found in environment variables")
        return None
    
    # Check rate limit
    within_limit, usage = check_rate_limit()
    if not within_limit:
        print(f"⚠️  Rate limit reached: {usage['monthly_count']}/{MAX_CALLS_PER_MONTH} calls this month")
        return None
    
    try:
        headers = {
            'x-access-token': GOLD_API_KEY,
            'Accept': 'application/json'
        }
        
        # Determine endpoint based on whether we want historical data
        if date_str:
            url = HISTORICAL_URL_PATTERN.format(date=date_str)
            print(f"📡 Fetching historical data from GoldAPI.io: {url}")
        else:
            url = API_BASE_URL
            print(f"📡 Fetching latest data from GoldAPI.io: {url}")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            record_api_call(url, success=True)
            print(f"✅ Successfully fetched data from GoldAPI.io")
            return data
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            record_api_call(url, success=False)
            return None
            
    except Exception as e:
        print(f"❌ Error fetching from GoldAPI.io: {e}")
        record_api_call(url if date_str else API_BASE_URL, success=False)
        return None


def fetch_from_fallback():
    """Fetch from free Thai Gold API as fallback."""
    try:
        print(f"📡 Fetching from fallback API: {FALLBACK_API}")
        response = requests.get(FALLBACK_API, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched data from fallback API")
            return data
        else:
            print(f"❌ Fallback API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching from fallback API: {e}")
        return None


def format_goldapi_data(api_data):
    """Format GoldAPI.io response for database import."""
    if not api_data or 'price' not in api_data:
        return None
    
    today = date.today()
    
    # Extract price data
    price = api_data.get('price', 0)
    open_price = api_data.get('open_price', price)
    high_price = api_data.get('high_price', price)
    low_price = api_data.get('low_price', price)
    close_price = api_data.get('close_price', price)
    
    # Create CSV row
    csv_row = {
        'date': today.strftime('%Y-%m-%d'),
        'commodity': 'GOLD',
        'symbol': 'XAU-THB',
        'price': price,
        'unit': 'oz',
        'open_price': open_price,
        'high_price': high_price,
        'low_price': low_price,
        'close_price': close_price,
        'volume': api_data.get('volume', 0)
    }
    
    return csv_row


def format_fallback_data(api_data):
    """Format fallback Thai Gold API response for database import."""
    if not api_data or 'response' not in api_data:
        return None
    
    response = api_data['response']
    price_data = response.get('price', {})
    
    # Thai gold API provides buy/sell prices for gold and gold bars
    # We'll use the average of buy/sell for the spot price
    gold_bar = price_data.get('gold_bar', {})
    buy_price = float(gold_bar.get('buy', '0').replace(',', ''))
    sell_price = float(gold_bar.get('sell', '0').replace(',', ''))
    
    # Calculate average spot price
    spot_price = (buy_price + sell_price) / 2
    
    today = date.today()
    
    csv_row = {
        'date': today.strftime('%Y-%m-%d'),
        'commodity': 'GOLD',
        'symbol': 'XAU-THB',
        'price': spot_price,
        'unit': 'baht',  # Thai gold is priced per baht weight
        'open_price': spot_price,
        'high_price': spot_price,
        'low_price': spot_price,
        'close_price': spot_price,
        'volume': 0
    }
    
    return csv_row


def save_to_csv(data, filename):
    """Save formatted data to CSV file."""
    df = pd.DataFrame([data])
    output_path = IMPORT_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"📁 Saved to: {output_path}")
    return output_path


def show_usage_stats():
    """Show current API usage statistics."""
    usage = load_usage_tracking()
    current_month = datetime.now().strftime('%Y-%m')
    
    print(f"\n📊 GoldAPI.io Usage Statistics:")
    print(f"   Current Month: {current_month}")
    print(f"   Calls Used: {usage['monthly_count']}/{MAX_CALLS_PER_MONTH}")
    print(f"   Calls Remaining: {MAX_CALLS_PER_MONTH - usage['monthly_count']}")
    
    if usage['calls']:
        print(f"   Last Call: {usage['calls'][-1]['timestamp']}")


def fetch_historical_data(start_date, end_date, max_calls=10):
    """Fetch historical Thai gold data for a date range.
    
    Args:
        start_date: Start date (datetime or date object)
        end_date: End date (datetime or date object) 
        max_calls: Maximum number of API calls to make (to preserve limit)
    
    Returns:
        List of historical data points
    """
    print(f"📅 Fetching historical data from {start_date} to {end_date}")
    print(f"⚠️  Limited to {max_calls} API calls to preserve monthly limit")
    
    # Load existing historical cache
    historical_data = []
    if HISTORICAL_CACHE_FILE.exists():
        with open(HISTORICAL_CACHE_FILE, 'r') as f:
            historical_data = json.load(f)
        print(f"📁 Found {len(historical_data)} existing historical records")
    
    # Generate list of dates to fetch
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    # Filter out dates we already have
    existing_dates = {item['date'] for item in historical_data}
    dates_to_fetch = [d for d in date_list if d.strftime('%Y-%m-%d') not in existing_dates]
    
    print(f"📊 Total dates in range: {len(date_list)}")
    print(f"✅ Already have: {len(date_list) - len(dates_to_fetch)}")
    print(f"🎯 Need to fetch: {len(dates_to_fetch)}")
    
    # Limit API calls
    dates_to_fetch = dates_to_fetch[:max_calls]
    print(f"⚠️  Will fetch {len(dates_to_fetch)} dates (limited to preserve API limit)")
    
    # Fetch data for each date
    for i, fetch_date in enumerate(dates_to_fetch, 1):
        date_str = fetch_date.strftime('%Y%m%d')
        print(f"\n[{i}/{len(dates_to_fetch)}] Fetching {fetch_date.strftime('%Y-%m-%d')}...")
        
        # Check rate limit before each call
        within_limit, usage = check_rate_limit()
        if not within_limit:
            print(f"⚠️  Rate limit reached - stopping historical fetch")
            break
        
        # Fetch data
        api_data = fetch_from_goldapi(date_str)
        
        if api_data:
            formatted = format_goldapi_data(api_data)
            if formatted:
                formatted['date'] = fetch_date.strftime('%Y-%m-%d')  # Ensure correct date
                historical_data.append(formatted)
                print(f"✅ Successfully fetched {fetch_date.strftime('%Y-%m-%d')}")
            else:
                print(f"❌ Failed to format data for {fetch_date.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ Failed to fetch {fetch_date.strftime('%Y-%m-%d')}")
    
    # Save updated historical data
    if historical_data:
        # Sort by date
        historical_data.sort(key=lambda x: x['date'])
        
        with open(HISTORICAL_CACHE_FILE, 'w') as f:
            json.dump(historical_data, f, indent=2)
        print(f"\n💾 Saved {len(historical_data)} total historical records to cache")
    
    return historical_data


def save_historical_to_csv(historical_data):
    """Save historical data to CSV file."""
    if not historical_data:
        print("❌ No historical data to save")
        return None
    
    df = pd.DataFrame(historical_data)
    output_path = IMPORT_DIR / 'thai_gold_historical.csv'
    df.to_csv(output_path, index=False)
    print(f"📁 Saved historical data to: {output_path}")
    print(f"📊 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"📈 Total records: {len(df)}")
    return output_path


def main():
    """Main function to download Thai gold prices."""
    parser = argparse.ArgumentParser(description='Download Thai gold prices from GoldAPI.io')
    parser.add_argument('--mode', choices=['latest', 'historical', 'test'], 
                       default='latest', help='Download mode: latest, historical, or test')
    parser.add_argument('--start-date', type=str, help='Start date for historical (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for historical (YYYY-MM-DD)')
    parser.add_argument('--max-calls', type=int, default=10, 
                       help='Maximum API calls for historical mode (default: 10)')
    parser.add_argument('--force', action='store_true', help='Force fetch ignoring cache')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("THAI GOLD PRICE DOWNLOADER")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    
    # Show current usage stats
    show_usage_stats()
    
    if args.mode == 'test':
        print("\n🧪 Testing API connectivity...")
        api_data = fetch_from_goldapi()
        if api_data:
            print("✅ API test successful!")
            print(f"📊 Sample data: {json.dumps(api_data, indent=2)[:500]}...")
        else:
            print("❌ API test failed")
        return
    
    elif args.mode == 'historical':
        # Historical mode
        if not args.start_date or not args.end_date:
            # Default to last 30 days if not specified
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            print(f"📅 No dates specified - using last 30 days")
        else:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        
        print(f"📅 Historical fetch: {start_date} to {end_date}")
        print(f"⚠️  Limited to {args.max_calls} API calls")
        
        historical_data = fetch_historical_data(start_date, end_date, args.max_calls)
        
        if historical_data:
            save_historical_to_csv(historical_data)
            print("✅ Historical data fetch complete")
        else:
            print("❌ No historical data fetched")
        return
    
    else:  # latest mode (default)
        # Check if it's a weekday
        if not is_weekday():
            print("⚠️  Today is a weekend - Thai gold markets are closed")
            print("   Using cached data if available...")
        
        # Check cache first (unless force flag)
        if not args.force and is_cache_fresh():
            print("✅ Using fresh cached data (less than 24 hours old)")
            cache = load_cache()
            cached_data = cache['data']
            
            # Format and save cached data
            if cached_data.get('source') == 'goldapi':
                formatted = format_goldapi_data(cached_data['api_data'])
            else:
                formatted = format_fallback_data(cached_data['api_data'])
            
            if formatted:
                save_to_csv(formatted, 'thai_gold_formatted.csv')
                print("✅ Import-ready file created from cache")
                return
        
        print("🔄 Cache is stale or empty - fetching fresh data...")
        
        # Try GoldAPI.io first
        api_data = fetch_from_goldapi()
        source = 'goldapi'
        
        # Fallback to free API if GoldAPI.io fails
        if not api_data:
            print("⚠️  GoldAPI.io failed - trying fallback API...")
            api_data = fetch_from_fallback()
            source = 'fallback'
        
        if api_data:
            # Cache the data
            cache_entry = {
                'source': source,
                'api_data': api_data
            }
            save_cache(cache_entry)
            
            # Format data based on source
            if source == 'goldapi':
                formatted = format_goldapi_data(api_data)
            else:
                formatted = format_fallback_data(api_data)
            
            if formatted:
                save_to_csv(formatted, 'thai_gold_formatted.csv')
                print("✅ Thai gold data downloaded and formatted successfully")
                
                # Show updated usage stats
                show_usage_stats()
            else:
                print("❌ Failed to format API data")
        else:
            print("❌ All data sources failed - no data available")


if __name__ == "__main__":
    main()