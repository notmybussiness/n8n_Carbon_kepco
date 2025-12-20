-- CarbonFlow Intelligence System - Schema v2
-- G2B API 응답 필드 기반 설계
-- KCH 그룹 유연탄 트레이딩 시스템

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 입찰 공고 테이블 (Tenders)
-- G2B API 필드명 그대로 사용 (원본 보존)
-- =====================================================
CREATE TABLE tenders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- G2B API 원본 필드
    bid_ntce_no VARCHAR(20) NOT NULL,           -- 입찰공고번호 (bidNtceNo)
    bid_ntce_ord VARCHAR(5) DEFAULT '00',       -- 입찰공고차수 (bidNtceOrd)
    bid_clsfc_no VARCHAR(20),                   -- 입찰분류번호 (bidClsfcNo)
    rbid_no VARCHAR(20),                        -- 재입찰번호 (rbidNo)
    ntce_div_cd VARCHAR(5),                     -- 공고구분코드 (ntceDivCd)
    bid_ntce_nm TEXT NOT NULL,                  -- 입찰공고명 (bidNtceNm)
    asign_bdgt_amt NUMERIC(15,2),               -- 배정예산금액 (asignBdgtAmt)
    presmpt_prce NUMERIC(15,2),                 -- 추정가격 (presmptPrce)
    bid_clse_dt TIMESTAMP WITH TIME ZONE,       -- 입찰마감일시 (bidClseDt)
    dminstt_nm VARCHAR(100),                    -- 수요기관명 (dminsttNm)
    dminstt_cd VARCHAR(20),                     -- 수요기관코드 (dminsttCd)
    bid_ntce_dtl_url TEXT,                      -- 공고상세URL (bidNtceDtlUrl)
    rgst_dt TIMESTAMP WITH TIME ZONE,           -- 등록일시 (rgstDt)
    
    -- 시스템 추가 필드
    source VARCHAR(20) NOT NULL DEFAULT 'G2B', -- 데이터 출처 (G2B, KEPCO, etc)
    ai_summary TEXT,                            -- AI 요약본
    relevance_score NUMERIC(3,2),               -- AI 관련도 점수 (0.00-1.00)
    status VARCHAR(20) DEFAULT 'OPEN',          -- OPEN, CLOSED, AWARDED
    raw_api_response JSONB,                     -- 원본 API 응답 (전체 보존)
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 복합 유니크 키 (출처 + 공고번호 + 차수)
    UNIQUE(source, bid_ntce_no, bid_ntce_ord)
);

-- =====================================================
-- 입찰 첨부파일 테이블 (Tender Attachments)
-- =====================================================
CREATE TABLE tender_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id UUID REFERENCES tenders(id) ON DELETE CASCADE,
    
    file_name VARCHAR(255) NOT NULL,            -- 파일명
    file_type VARCHAR(20),                      -- hwp, hwpx, pdf, xlsx
    file_url TEXT,                              -- 다운로드 URL
    file_size_bytes INTEGER,                    -- 파일 크기
    
    extracted_text TEXT,                        -- 추출된 텍스트 전문
    is_parsed BOOLEAN DEFAULT FALSE,            -- 파싱 완료 여부
    parse_error TEXT,                           -- 파싱 에러 메시지
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 입찰 스펙 테이블 (Tender Specs)
-- HWP 파싱 결과 저장
-- =====================================================
CREATE TABLE tender_specs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id UUID REFERENCES tenders(id) ON DELETE CASCADE,
    
    commodity_type VARCHAR(50) DEFAULT 'Thermal Coal',
    
    -- 발열량 스펙
    cv_min_kcal INTEGER,                        -- 최소 발열량 (kcal/kg)
    cv_max_kcal INTEGER,                        -- 최대 발열량
    cv_basis VARCHAR(10),                       -- NAR, GAR, ADB
    
    -- 품질 스펙
    sulfur_max_pct NUMERIC(4,2),                -- 최대 황분 (%)
    ash_max_pct NUMERIC(4,2),                   -- 최대 회분 (%)
    moisture_max_pct NUMERIC(4,2),              -- 최대 수분 (%)
    
    -- 물량 및 조건
    quantity_mt NUMERIC(12,2),                  -- 물량 (MT)
    origin VARCHAR(100),                        -- 원산지 (인도네시아, 호주 등)
    incoterms VARCHAR(10),                      -- FOB, CIF, CFR
    delivery_port VARCHAR(100),                 -- 납품항
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 선박 운항 정보 테이블 (Shipments)
-- =====================================================
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    vessel_name VARCHAR(100) NOT NULL,          -- 선박명
    mmsi VARCHAR(20),                           -- MMSI 번호
    imo_number VARCHAR(20),                     -- IMO 번호
    voyage_number VARCHAR(50),                  -- 항차 번호
    
    cargo_qty_mt NUMERIC(12,2),                 -- 화물량 (MT)
    loading_port VARCHAR(100),                  -- 선적항
    discharge_port VARCHAR(100),                -- 하역항
    
    laycan_start DATE,                          -- Laycan 시작일
    laycan_end DATE,                            -- Laycan 종료일
    eta TIMESTAMP WITH TIME ZONE,               -- 입항 예정 시간
    etb TIMESTAMP WITH TIME ZONE,               -- 접안 예정 시간
    
    current_status VARCHAR(30),                 -- SAILING, WAITING, BERTHED, etc
    current_lat NUMERIC(10,6),                  -- 현재 위도
    current_lng NUMERIC(10,6),                  -- 현재 경도
    last_position_at TIMESTAMP WITH TIME ZONE,  -- 위치 갱신 시각
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 체선료 계산 테이블 (Demurrage Calculations)
-- =====================================================
CREATE TABLE demurrage_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shipment_id UUID REFERENCES shipments(id) ON DELETE CASCADE,
    
    contract_laytime_hrs NUMERIC(10,2),         -- 계약상 허용 시간
    actual_laytime_hrs NUMERIC(10,2),           -- 실제 사용 시간
    weather_delay_hrs NUMERIC(10,2) DEFAULT 0,  -- 기상 지연 시간
    
    dem_rate_daily_usd NUMERIC(12,2),           -- 일일 체선료 (USD)
    total_demurrage_usd NUMERIC(12,2),          -- 총 체선료
    total_despatch_usd NUMERIC(12,2),           -- 총 조출료
    
    calculation_log JSONB,                      -- 상세 계산 내역
    sof_file_url TEXT,                          -- SOF 파일 URL
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 시장 데이터 테이블 (Market Data)
-- =====================================================
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    data_date DATE NOT NULL,
    index_name VARCHAR(50) NOT NULL,            -- Newcastle, ICI4, Indonesian
    price_usd NUMERIC(10,2),                    -- USD/MT
    fx_rate_krw NUMERIC(10,4),                  -- KRW/USD 환율
    freight_rate NUMERIC(10,2),                 -- 해상 운임
    source VARCHAR(100),                        -- 데이터 출처
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(data_date, index_name)
);

-- =====================================================
-- Netback 시뮬레이션 테이블
-- =====================================================
CREATE TABLE netback_simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id UUID REFERENCES tenders(id) ON DELETE SET NULL,
    
    simulation_date DATE NOT NULL,
    market_price_usd NUMERIC(10,2),
    freight_cost NUMERIC(10,2),
    insurance_cost NUMERIC(10,2),
    port_charges NUMERIC(10,2),
    import_duty NUMERIC(10,2),
    fx_rate NUMERIC(10,4),
    
    netback_usd NUMERIC(10,2),                  -- 예상 순수익 (USD/MT)
    netback_krw NUMERIC(12,2),                  -- 예상 순수익 (KRW/MT)
    assumptions JSONB,                          -- 가정 조건
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- Indexes
-- =====================================================
CREATE INDEX idx_tenders_source ON tenders(source);
CREATE INDEX idx_tenders_bid_ntce_no ON tenders(bid_ntce_no);
CREATE INDEX idx_tenders_bid_clse_dt ON tenders(bid_clse_dt);
CREATE INDEX idx_tenders_status ON tenders(status);
CREATE INDEX idx_tenders_dminstt_nm ON tenders(dminstt_nm);

CREATE INDEX idx_attachments_tender_id ON tender_attachments(tender_id);
CREATE INDEX idx_specs_tender_id ON tender_specs(tender_id);

CREATE INDEX idx_shipments_vessel ON shipments(vessel_name);
CREATE INDEX idx_shipments_status ON shipments(current_status);

CREATE INDEX idx_market_data_date ON market_data(data_date);
CREATE INDEX idx_market_data_index ON market_data(index_name);

-- =====================================================
-- Row Level Security (RLS)
-- =====================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN;
    END IF;
END $$;

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- Updated At Trigger
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tenders_updated_at
    BEFORE UPDATE ON tenders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shipments_updated_at
    BEFORE UPDATE ON shipments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
