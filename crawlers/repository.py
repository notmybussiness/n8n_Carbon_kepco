import os
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from pydantic import BaseModel

# DTO imports (assuming they are in the same package or accessible)
try:
    from dto import TenderDTO, TenderAttachmentDTO, TenderSpecDTO, TenderStatus, ShipmentDTO, ShipmentStatus, DemurrageCalcDTO, MarketDataDTO, NetbackSimulationDTO
except ImportError:
    # For standalone testing if imports fail relative to path
    from crawlers.dto import TenderDTO, TenderAttachmentDTO, TenderSpecDTO, TenderStatus, ShipmentDTO, ShipmentStatus, DemurrageCalcDTO, MarketDataDTO, NetbackSimulationDTO

class SupabaseRepository:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)

    def upsert_tender(self, tender: TenderDTO) -> Dict[str, Any]:
        """
        Tender 데이터를 Upsert 합니다.
        (source, bid_ntce_no, bid_ntce_ord) 조합이 Unique Key입니다.
        """
        # DTO to Dict conversion
        data = {
            "bid_ntce_no": tender.bid_ntce_no,
            "bid_ntce_ord": tender.bid_ntce_ord,
            "source": tender.source.value if hasattr(tender.source, 'value') else tender.source,
            "bid_ntce_nm": tender.bid_ntce_nm,
            "ntce_div_cd": tender.ntce_div_cd,
            "dminstt_nm": tender.dminstt_nm,
            "dminstt_cd": tender.dminstt_cd,
            "asign_bdgt_amt": tender.asign_bdgt_amt,
            "presmpt_prce": tender.presmpt_prce,
            "bid_clse_dt": tender.bid_clse_dt.isoformat() if tender.bid_clse_dt else None,
            "bid_ntce_dtl_url": tender.bid_ntce_dtl_url,
            "status": tender.status.value if hasattr(tender.status, 'value') else tender.status,
            "raw_api_response": tender.raw_api_response,
            "ai_summary": tender.ai_summary,
            "relevance_score": tender.relevance_score,
            # created_at and updated_at are handled by DB triggers, 
            # but we can optionally send them if we want to force a specific time.
            # Generally better to let DB handle it on insert, and maybe updated_at on update.
        }

        # Remove None values if you want default behavior, or keep them to set NULL
        # For upsert, we need to handle the conflict.
        
        response = self.supabase.table("tenders").upsert(
            data, 
            on_conflict="source, bid_ntce_no, bid_ntce_ord"
        ).execute()
        
        return response.data[0] if response.data else None

    def get_tender_by_id(self, tender_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("tenders").select("*").eq("id", tender_id).execute()
        return response.data[0] if response.data else None
        
    def get_tender_by_notice_no(self, source: str, bid_ntce_no: str, bid_ntce_ord: str = "00") -> Optional[Dict[str, Any]]:
        response = self.supabase.table("tenders").select("*")\
            .eq("source", source)\
            .eq("bid_ntce_no", bid_ntce_no)\
            .eq("bid_ntce_ord", bid_ntce_ord)\
            .execute()
        return response.data[0] if response.data else None

    def upsert_attachment(self, attachment: TenderAttachmentDTO) -> Dict[str, Any]:
        data = {
            "tender_id": attachment.tender_id,
            "file_name": attachment.file_name,
            "file_type": attachment.file_type,
            "file_url": attachment.file_url,
            "extracted_text": attachment.extracted_text,
            "is_parsed": attachment.is_parsed
        }
        
        # If ID exists, we can use it to update, otherwise insert.
        # However, attachments don't have a natural unique key other than ID.
        # If we want to avoid duplicates, we might verify by file_url or name + tender_id.
        # For now, simplistic insert unless ID is provided.
        
        if attachment.id:
            data["id"] = attachment.id
            response = self.supabase.table("tender_attachments").upsert(data).execute()
        else:
            # Check existance by filename + tender_id to prevent duplicates on re-runs
            existing = self.supabase.table("tender_attachments").select("id")\
                .eq("tender_id", attachment.tender_id)\
                .eq("file_name", attachment.file_name)\
                .execute()
            
            if existing.data:
                data["id"] = existing.data[0]["id"]
                response = self.supabase.table("tender_attachments").upsert(data).execute()
            else:
                response = self.supabase.table("tender_attachments").insert(data).execute()
                
        return response.data[0] if response.data else None

    def get_attachments_by_tender_id(self, tender_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("tender_attachments").select("*").eq("tender_id", tender_id).execute()
        return response.data

    def upsert_tender_spec(self, spec: TenderSpecDTO) -> Dict[str, Any]:
        data = {
            "tender_id": spec.tender_id,
            "commodity_type": spec.commodity_type,
            "cv_min_kcal": spec.cv_min_kcal,
            "cv_max_kcal": spec.cv_max_kcal,
            "cv_basis": spec.cv_basis.value if hasattr(spec.cv_basis, 'value') else spec.cv_basis,
            "sulfur_max_pct": spec.sulfur_max_pct,
            "ash_max_pct": spec.ash_max_pct,
            "moisture_max_pct": spec.moisture_max_pct,
            "quantity_mt": spec.quantity_mt,
            "origin": spec.origin,
            "incoterms": spec.incoterms.value if hasattr(spec.incoterms, 'value') else spec.incoterms,
            "delivery_port": spec.delivery_port
        }

        if spec.id:
            data["id"] = spec.id
            response = self.supabase.table("tender_specs").upsert(data).execute()
        else:
            # Check if spec exists for this tender (One-to-One or One-to-Many logic?)
            # Usually one spec per tender, but current schema allows many if not constrained.
            # Assuming logic: One spec per tender mostly.
            existing = self.supabase.table("tender_specs").select("id").eq("tender_id", spec.tender_id).execute()
            
            if existing.data:
                data["id"] = existing.data[0]["id"]
                response = self.supabase.table("tender_specs").upsert(data).execute()
            else:
                response = self.supabase.table("tender_specs").insert(data).execute()
                
        return response.data[0] if response.data else None

    def get_tender_spec_by_tender_id(self, tender_id: str) -> Optional[Dict[str, Any]]:
        # Returns the first spec found
        response = self.supabase.table("tender_specs").select("*").eq("tender_id", tender_id).execute()
        return response.data[0] if response.data else None

    # =====================================================
    # Shipments
    # =====================================================

    def upsert_shipment(self, shipment: ShipmentDTO) -> Dict[str, Any]:
        data = {
            "vessel_name": shipment.vessel_name,
            "mmsi": shipment.mmsi,
            "imo_number": shipment.imo_number,
            "voyage_number": shipment.voyage_number,
            "cargo_qty_mt": shipment.cargo_qty_mt,
            "loading_port": shipment.loading_port,
            "discharge_port": shipment.discharge_port,
            "laycan_start": shipment.laycan_start.isoformat() if shipment.laycan_start else None,
            "laycan_end": shipment.laycan_end.isoformat() if shipment.laycan_end else None,
            "eta": shipment.eta.isoformat() if shipment.eta else None,
            "etb": shipment.etb.isoformat() if shipment.etb else None,
            "current_status": shipment.current_status.value if hasattr(shipment.current_status, 'value') else shipment.current_status,
            "current_lat": shipment.current_lat,
            "current_lng": shipment.current_lng,
            "last_position_at": shipment.last_position_at.isoformat() if shipment.last_position_at else None
        }

        if shipment.id:
            data["id"] = shipment.id
            response = self.supabase.table("shipments").upsert(data).execute()
        else:
            # Maybe check by vessel_name + voyage_number?
            response = self.supabase.table("shipments").insert(data).execute()
            
        return response.data[0] if response.data else None

    def get_shipment_by_id(self, shipment_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("shipments").select("*").eq("id", shipment_id).execute()
        return response.data[0] if response.data else None

    # =====================================================
    # Demurrage Calculations
    # =====================================================

    def upsert_demurrage_calc(self, calc: DemurrageCalcDTO) -> Dict[str, Any]:
        data = {
            "shipment_id": calc.shipment_id,
            "contract_laytime_hrs": calc.contract_laytime_hrs,
            "actual_laytime_hrs": calc.actual_laytime_hrs,
            "weather_delay_hrs": calc.weather_delay_hrs,
            "dem_rate_daily_usd": calc.dem_rate_daily_usd,
            "total_demurrage_usd": calc.total_demurrage_usd,
            "total_despatch_usd": calc.total_despatch_usd,
            "calculation_log": calc.calculation_log,
            "sof_file_url": calc.sof_file_url
        }
        
        if calc.id:
            data["id"] = calc.id
            response = self.supabase.table("demurrage_calculations").upsert(data).execute()
        else:
             response = self.supabase.table("demurrage_calculations").insert(data).execute()
             
        return response.data[0] if response.data else None
        
    def get_demurrage_by_shipment_id(self, shipment_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("demurrage_calculations").select("*").eq("shipment_id", shipment_id).execute()
        return response.data

    # =====================================================
    # Market Data
    # =====================================================

    def upsert_market_data(self, data: MarketDataDTO) -> Dict[str, Any]:
        payload = {
            "data_date": data.data_date.isoformat() if data.data_date else None,
            "index_name": data.index_name,
            "price_usd": data.price_usd,
            "fx_rate_krw": data.fx_rate_krw,
            "freight_rate": data.freight_rate,
            "source": data.source
        }
        
        # Unique key: data_date + index_name
        response = self.supabase.table("market_data").upsert(
            payload,
            on_conflict="data_date, index_name"
        ).execute()
        
        return response.data[0] if response.data else None

    def get_market_data(self, data_date: date, index_name: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("market_data").select("*")\
            .eq("data_date", data_date.isoformat())\
            .eq("index_name", index_name)\
            .execute()
        return response.data[0] if response.data else None

    # =====================================================
    # Netback Simulations
    # =====================================================

    def upsert_netback_simulation(self, sim: NetbackSimulationDTO) -> Dict[str, Any]:
        data = {
            "tender_id": sim.tender_id,
            "simulation_date": sim.simulation_date.isoformat() if sim.simulation_date else None,
            "market_price_usd": sim.market_price_usd,
            "freight_cost": sim.freight_cost,
            "insurance_cost": sim.insurance_cost,
            "port_charges": sim.port_charges,
            "import_duty": sim.import_duty,
            "fx_rate": sim.fx_rate,
            "netback_usd": sim.netback_usd,
            "netback_krw": sim.netback_krw,
            "assumptions": sim.assumptions
        }

        if sim.id:
            data["id"] = sim.id
            response = self.supabase.table("netback_simulations").upsert(data).execute()
        else:
            response = self.supabase.table("netback_simulations").insert(data).execute()
            
        return response.data[0] if response.data else None

    def get_netback_simulation_by_id(self, sim_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("netback_simulations").select("*").eq("id", sim_id).execute()
        return response.data[0] if response.data else None
    
    def get_simulations_by_tender_id(self, tender_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("netback_simulations").select("*").eq("tender_id", tender_id).execute()
        return response.data


