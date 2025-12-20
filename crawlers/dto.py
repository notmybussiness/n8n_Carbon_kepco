"""
CarbonFlow DTO (Data Transfer Objects)
실제 API 응답 필드를 기반으로 설계된 데이터 모델
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


# =====================================================
# Enums
# =====================================================

class TenderSource(str, Enum):
    """입찰 공고 출처"""
    G2B = "G2B"           # 나라장터
    KEPCO = "KEPCO"       # 한전SRM
    KOWEPO = "KOWEPO"     # 서부발전
    KOSPO = "KOSPO"       # 남부발전
    KOMIPO = "KOMIPO"     # 중부발전
    KOEN = "KOEN"         # 남동발전
    EWP = "EWP"           # 동서발전


class TenderStatus(str, Enum):
    """입찰 공고 상태"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    AWARDED = "AWARDED"
    CANCELLED = "CANCELLED"


class ShipmentStatus(str, Enum):
    """선박 운항 상태"""
    SCHEDULED = "SCHEDULED"
    LOADING = "LOADING"
    SAILING = "SAILING"
    WAITING = "WAITING"
    BERTHED = "BERTHED"
    DISCHARGING = "DISCHARGING"
    COMPLETED = "COMPLETED"


class CVBasis(str, Enum):
    """발열량 기준"""
    NAR = "NAR"  # Net As Received
    GAR = "GAR"  # Gross As Received
    ADB = "ADB"  # Air Dried Basis


class Incoterms(str, Enum):
    """인코텀즈"""
    FOB = "FOB"
    CIF = "CIF"
    CFR = "CFR"
    DES = "DES"
    DAP = "DAP"


# =====================================================
# G2B API Response DTO
# (실제 API 응답 필드 기반)
# =====================================================

@dataclass
class G2BApiResponse:
    """
    나라장터 입찰공고 API 응답 DTO
    getBidPblancListInfoThng 오퍼레이션 기준
    """
    # 입찰 기본 정보
    bidNtceNo: str                          # 입찰공고번호 (PK)
    bidNtceOrd: str = ""                    # 입찰공고차수
    bidClsfcNo: str = ""                    # 입찰분류번호
    rbidNo: str = ""                        # 재입찰번호
    
    # 공고 정보
    ntceDivCd: str = ""                     # 공고구분코드 (1=조달청, 2=자체 등)
    bidNtceNm: str = ""                     # 입찰공고명
    
    # 금액 정보
    asignBdgtAmt: Optional[float] = None    # 배정예산금액
    presmptPrce: Optional[float] = None     # 추정가격
    
    # 일시 정보
    bidClseDt: Optional[str] = None         # 입찰마감일시 (YYYY/MM/DD HH:MM)
    rgstDt: Optional[str] = None            # 등록일시
    
    # 기관 정보
    dminsttNm: Optional[str] = None         # 수요기관명
    dminsttCd: Optional[str] = None         # 수요기관코드
    
    # URL
    bidNtceDtlUrl: Optional[str] = None     # 공고상세URL
    
    # 원본 데이터
    raw_response: Dict[str, Any] = field(default_factory=dict)


# =====================================================
# Domain DTOs
# =====================================================

@dataclass
class TenderDTO:
    """입찰 공고 DTO"""
    id: Optional[str] = None
    bid_ntce_no: str = ""                   # 입찰공고번호
    bid_ntce_ord: str = ""                  # 입찰공고차수
    source: TenderSource = TenderSource.G2B
    bid_ntce_nm: str = ""                   # 입찰공고명
    ntce_div_cd: str = ""                   # 공고구분코드
    dminstt_nm: Optional[str] = None        # 수요기관명
    dminstt_cd: Optional[str] = None        # 수요기관코드
    asign_bdgt_amt: Optional[float] = None  # 배정예산금액
    presmpt_prce: Optional[float] = None    # 추정가격
    bid_clse_dt: Optional[datetime] = None  # 입찰마감일시
    bid_ntce_dtl_url: Optional[str] = None  # 공고상세URL
    ai_summary: Optional[str] = None        # AI 요약
    relevance_score: Optional[float] = None # 관련도 점수 (0.0~1.0)
    status: TenderStatus = TenderStatus.OPEN
    raw_api_response: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_g2b_api(cls, api_response: G2BApiResponse) -> "TenderDTO":
        """G2B API 응답에서 TenderDTO 생성"""
        bid_clse_dt = None
        if api_response.bidClseDt:
            try:
                bid_clse_dt = datetime.strptime(
                    api_response.bidClseDt, "%Y/%m/%d %H:%M"
                )
            except ValueError:
                pass
        
        return cls(
            bid_ntce_no=api_response.bidNtceNo,
            bid_ntce_ord=api_response.bidNtceOrd,
            source=TenderSource.G2B,
            bid_ntce_nm=api_response.bidNtceNm,
            ntce_div_cd=api_response.ntceDivCd,
            dminstt_nm=api_response.dminsttNm,
            dminstt_cd=api_response.dminsttCd,
            asign_bdgt_amt=api_response.asignBdgtAmt,
            presmpt_prce=api_response.presmptPrce,
            bid_clse_dt=bid_clse_dt,
            bid_ntce_dtl_url=api_response.bidNtceDtlUrl,
            status=TenderStatus.OPEN,
            raw_api_response=api_response.raw_response,
            created_at=datetime.now()
        )


@dataclass
class TenderAttachmentDTO:
    """입찰 공고 첨부파일 DTO"""
    id: Optional[str] = None
    tender_id: str = ""
    file_name: str = ""
    file_type: str = ""                     # hwp, hwpx, pdf, etc.
    file_url: Optional[str] = None
    extracted_text: Optional[str] = None
    is_parsed: bool = False
    created_at: Optional[datetime] = None


@dataclass
class TenderSpecDTO:
    """입찰 공고 스펙 DTO (HWP 파싱 결과)"""
    id: Optional[str] = None
    tender_id: str = ""
    commodity_type: str = "Thermal Coal"
    cv_min_kcal: Optional[int] = None       # 최소 발열량 (kcal/kg)
    cv_max_kcal: Optional[int] = None       # 최대 발열량
    cv_basis: CVBasis = CVBasis.NAR
    sulfur_max_pct: Optional[float] = None  # 최대 황분 (%)
    ash_max_pct: Optional[float] = None     # 최대 회분 (%)
    moisture_max_pct: Optional[float] = None # 최대 수분 (%)
    quantity_mt: Optional[float] = None     # 물량 (MT)
    origin: Optional[str] = None            # 원산지
    incoterms: Optional[Incoterms] = None
    delivery_port: Optional[str] = None     # 납품항
    created_at: Optional[datetime] = None


@dataclass
class ShipmentDTO:
    """선박 운항 정보 DTO"""
    id: Optional[str] = None
    vessel_name: str = ""
    mmsi: Optional[str] = None
    imo_number: Optional[str] = None
    voyage_number: Optional[str] = None
    cargo_qty_mt: Optional[float] = None
    loading_port: Optional[str] = None
    discharge_port: Optional[str] = None
    laycan_start: Optional[date] = None
    laycan_end: Optional[date] = None
    eta: Optional[datetime] = None
    etb: Optional[datetime] = None
    current_status: ShipmentStatus = ShipmentStatus.SCHEDULED
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    last_position_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class DemurrageCalcDTO:
    """체선료 계산 DTO"""
    id: Optional[str] = None
    shipment_id: str = ""
    contract_laytime_hrs: Optional[float] = None
    actual_laytime_hrs: Optional[float] = None
    weather_delay_hrs: float = 0.0
    dem_rate_daily_usd: Optional[float] = None
    total_demurrage_usd: Optional[float] = None
    total_despatch_usd: Optional[float] = None
    calculation_log: Dict[str, Any] = field(default_factory=dict)
    sof_file_url: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class MarketDataDTO:
    """시장 데이터 DTO"""
    id: Optional[str] = None
    data_date: date = None
    index_name: str = ""                    # Newcastle, ICI4, etc.
    price_usd: Optional[float] = None       # USD/MT
    fx_rate_krw: Optional[float] = None     # KRW/USD 환율
    freight_rate: Optional[float] = None    # 해상 운임
    source: Optional[str] = None            # Argus, McCloskey
    created_at: Optional[datetime] = None


@dataclass
class NetbackSimulationDTO:
    """Netback 시뮬레이션 DTO"""
    id: Optional[str] = None
    tender_id: Optional[str] = None
    simulation_date: date = None
    market_price_usd: Optional[float] = None
    freight_cost: Optional[float] = None
    insurance_cost: Optional[float] = None
    port_charges: Optional[float] = None
    import_duty: Optional[float] = None
    fx_rate: Optional[float] = None
    netback_usd: Optional[float] = None     # 예상 순수익 (USD/MT)
    netback_krw: Optional[float] = None     # 예상 순수익 (KRW/MT)
    assumptions: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
