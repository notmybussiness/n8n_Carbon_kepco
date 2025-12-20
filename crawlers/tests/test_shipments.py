"""
Test script for Shipment CRUD operations
Requires: SUPABASE_URL and SUPABASE_KEY environment variables
"""
import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dto import ShipmentDTO, DemurrageCalcDTO, ShipmentStatus
from repository import SupabaseRepository

# Supabase Credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

def test_shipment_crud():
    print("=== Testing Shipment CRUD ===")
    repo = SupabaseRepository(SUPABASE_URL, SUPABASE_KEY)
    
    # Create Shipment
    shipment = ShipmentDTO(
        vessel_name="MV Test Carrier",
        imo_number="1234567",
        origin_port="Newcastle",
        dest_port="Incheon",
        eta=datetime(2024, 12, 25, 10, 0),
        status=ShipmentStatus.LOADING,
        cargo_mt=75000.0
    )
    
    result = repo.upsert_shipment(shipment)
    print(f"Shipment ID: {result['id']}")
    shipment_id = result['id']
    
    # Create Demurrage Calc
    print("\n=== Testing Demurrage CRUD ===")
    demurrage = DemurrageCalcDTO(
        shipment_id=shipment_id,
        calculation_date=date.today(),
        allowed_days=5.0,
        actual_days=7.5,
        demurrage_rate=25000.0
    )
    
    dem_result = repo.upsert_demurrage_calc(demurrage)
    print(f"Demurrage ID: {dem_result['id']}")
    
    # Validate
    fetched = repo.get_demurrage_by_shipment_id(shipment_id)
    assert len(fetched) >= 1
    print("Demurrage verification successful!")

if __name__ == "__main__":
    try:
        test_shipment_crud()
        print("\nAll Tests Passed!")
    except Exception as e:
        print(f"\nTests Failed: {e}")
        import traceback
        traceback.print_exc()
