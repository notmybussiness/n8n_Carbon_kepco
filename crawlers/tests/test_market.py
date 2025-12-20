"""
Test script for Market Data CRUD operations
Requires: SUPABASE_URL and SUPABASE_KEY environment variables
"""
import os
import sys
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dto import MarketDataDTO
from repository import SupabaseRepository

# Supabase Credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

def test_market_data_crud():
    print("=== Testing Market Data CRUD ===")
    repo = SupabaseRepository(SUPABASE_URL, SUPABASE_KEY)
    
    # Create Market Data
    market = MarketDataDTO(
        data_date=date.today(),
        index_name="Newcastle FOB",
        price=132.50,
        currency="USD",
        unit="MT"
    )
    
    result = repo.upsert_market_data(market)
    print(f"Market Data ID: {result['id']}")
    
    # Validate
    fetched = repo.get_market_data(date.today(), "Newcastle FOB")
    assert fetched['price'] == 132.50
    print("Market data verification successful!")

if __name__ == "__main__":
    try:
        test_market_data_crud()
        print("\nAll Tests Passed!")
    except Exception as e:
        print(f"\nTests Failed: {e}")
        import traceback
        traceback.print_exc()
