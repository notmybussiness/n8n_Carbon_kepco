"""
Test script for Netback Simulation CRUD operations
Requires: SUPABASE_URL and SUPABASE_KEY environment variables
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dto import NetbackSimulationDTO
from repository import SupabaseRepository

# Supabase Credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

def test_simulation_crud():
    print("=== Testing Netback Simulation CRUD ===")
    repo = SupabaseRepository(SUPABASE_URL, SUPABASE_KEY)
    
    # First create a tender for the simulation
    from dto import TenderDTO, TenderSource
    tender = TenderDTO(
        bid_ntce_no=f"SIM-TEST-{int(datetime.now().timestamp())}",
        bid_ntce_ord="00",
        source=TenderSource.KEPCO,
        bid_ntce_nm="Simulation Test Tender"
    )
    tender_result = repo.upsert_tender(tender)
    tender_id = tender_result['id']
    print(f"Created test tender: {tender_id}")
    
    # Create Simulation
    simulation = NetbackSimulationDTO(
        tender_id=tender_id,
        origin_port="Newcastle",
        index_price=130.00,
        freight_rate=15.50,
        insurance_rate=0.25,
        other_costs=2.00,
        netback_price=112.25
    )
    
    result = repo.upsert_netback_simulation(simulation)
    print(f"Simulation ID: {result['id']}")
    
    # Validate
    fetched = repo.get_simulations_by_tender_id(tender_id)
    assert len(fetched) >= 1
    assert fetched[0]['netback_price'] == 112.25
    print("Simulation verification successful!")

if __name__ == "__main__":
    try:
        test_simulation_crud()
        print("\nAll Tests Passed!")
    except Exception as e:
        print(f"\nTests Failed: {e}")
        import traceback
        traceback.print_exc()
