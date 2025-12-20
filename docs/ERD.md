# CarbonFlow ERD (Entity Relationship Diagram)

본 문서는 실제 공공데이터포털 API 응답 구조를 분석하여 설계한 데이터베이스 ERD입니다.

---

## 데이터 소스 분석

### G2B (나라장터) API 응답 필드
`getBidPblancListInfoThng` 오퍼레이션 기준:

| API 필드명 | 한글명 | 데이터 타입 | 비고 |
|-----------|--------|------------|------|
| bidNtceNo | 입찰공고번호 | VARCHAR | PK, 예: "20160439522" |
| bidNtceOrd | 입찰공고차수 | VARCHAR | 예: "00" |
| bidClsfcNo | 입찰분류번호 | VARCHAR | |
| rbidNo | 재입찰번호 | VARCHAR | |
| ntceDivCd | 공고구분코드 | VARCHAR | 1=조달청, 2=자체 등 |
| bidNtceNm | 입찰공고명 | TEXT | 공고 제목 |
| asignBdgtAmt | 배정예산금액 | NUMERIC | 설계 금액 |
| presmptPrce | 추정가격 | NUMERIC | |
| bidClseDt | 입찰마감일시 | TIMESTAMP | |
| dminsttNm | 수요기관명 | VARCHAR | 발주처 |
| dminsttCd | 수요기관코드 | VARCHAR | |
| bidNtceDtlUrl | 공고상세URL | TEXT | 상세페이지 링크 |
| rgstDt | 등록일시 | TIMESTAMP | |

---

## ERD Diagram

```mermaid
erDiagram
    TENDERS ||--o{ TENDER_ATTACHMENTS : has
    TENDERS ||--o{ TENDER_SPECS : contains
    SHIPMENTS ||--o{ DEMURRAGE_CALCS : calculates
    MARKET_DATA ||--o{ NETBACK_SIMULATIONS : uses
    TENDERS ||--o{ NETBACK_SIMULATIONS : references

    TENDERS {
        uuid id PK
        varchar bid_ntce_no UK "입찰공고번호 (API)"
        varchar bid_ntce_ord "입찰공고차수"
        varchar source "G2B, KEPCO, etc"
        text bid_ntce_nm "입찰공고명"
        varchar ntce_div_cd "공고구분코드"
        varchar dminstt_nm "수요기관명"
        varchar dminstt_cd "수요기관코드"
        numeric asign_bdgt_amt "배정예산금액"
        numeric presmpt_prce "추정가격"
        timestamp bid_clse_dt "입찰마감일시"
        text bid_ntce_dtl_url "공고상세URL"
        text ai_summary "AI 요약"
        numeric relevance_score "관련도점수"
        varchar status "OPEN/CLOSED/AWARDED"
        jsonb raw_api_response "원본 API 응답"
        timestamp created_at
        timestamp updated_at
    }

    TENDER_ATTACHMENTS {
        uuid id PK
        uuid tender_id FK
        varchar file_name "파일명"
        varchar file_type "hwp, pdf, etc"
        text file_url "다운로드 URL"
        text extracted_text "추출된 텍스트"
        boolean is_parsed "파싱 완료여부"
        timestamp created_at
    }

    TENDER_SPECS {
        uuid id PK
        uuid tender_id FK
        varchar commodity_type "Thermal Coal"
        integer cv_min_kcal "최소 발열량"
        integer cv_max_kcal "최대 발열량"
        varchar cv_basis "NAR/GAR"
        numeric sulfur_max_pct "최대 황분"
        numeric ash_max_pct "최대 회분"
        numeric moisture_max_pct "최대 수분"
        numeric quantity_mt "물량(MT)"
        varchar origin "원산지"
        varchar incoterms "FOB/CIF/CFR"
        varchar delivery_port "납품항"
        timestamp created_at
    }

    SHIPMENTS {
        uuid id PK
        varchar vessel_name "선박명"
        varchar mmsi "MMSI"
        varchar imo_number "IMO"
        varchar voyage_number "항차번호"
        numeric cargo_qty_mt "화물량(MT)"
        varchar loading_port "선적항"
        varchar discharge_port "하역항"
        date laycan_start "Laycan 시작"
        date laycan_end "Laycan 종료"
        timestamp eta "입항예정"
        timestamp etb "접안예정"
        varchar current_status "운항상태"
        numeric current_lat "현재위도"
        numeric current_lng "현재경도"
        timestamp last_position_at "위치갱신시각"
        timestamp created_at
        timestamp updated_at
    }

    DEMURRAGE_CALCS {
        uuid id PK
        uuid shipment_id FK
        numeric contract_laytime_hrs "계약 허용시간"
        numeric actual_laytime_hrs "실제 사용시간"
        numeric weather_delay_hrs "기상지연시간"
        numeric dem_rate_daily_usd "일일체선료"
        numeric total_demurrage_usd "총체선료"
        numeric total_despatch_usd "총조출료"
        jsonb calculation_log "계산내역"
        text sof_file_url "SOF 파일"
        timestamp created_at
    }

    MARKET_DATA {
        uuid id PK
        date data_date UK
        varchar index_name UK "Newcastle, ICI4"
        numeric price_usd "USD/MT"
        numeric fx_rate_krw "KRW/USD"
        numeric freight_rate "해상운임"
        varchar source "Argus, McCloskey"
        timestamp created_at
    }

    NETBACK_SIMULATIONS {
        uuid id PK
        uuid tender_id FK
        date simulation_date
        numeric market_price_usd
        numeric freight_cost
        numeric insurance_cost
        numeric port_charges
        numeric import_duty
        numeric fx_rate
        numeric netback_usd "예상순수익"
        numeric netback_krw
        jsonb assumptions "가정조건"
        timestamp created_at
    }
```

---

## 설계 원칙

1. **API 원본 보존**: `raw_api_response` 필드로 원본 JSON 저장
2. **정규화**: 첨부파일과 스펙은 별도 테이블로 분리
3. **확장성**: JSONB 필드로 미래 필드 추가 대응
4. **추적성**: 모든 테이블에 `created_at`, `updated_at` 포함
