# 공공데이터포털 API 응답 구조 분석

이 문서는 CarbonFlow 시스템 개발에 사용되는 API 응답 구조를 정리한 것입니다.

---

## 1. 나라장터 입찰공고 API

### 기본 정보
- **서비스명**: 나라장터 입찰공고정보서비스
- **오퍼레이션**: `getBidPblancListInfoThng` (물품 입찰공고 목록 조회)
- **Base URL**: `http://apis.data.go.kr/1230000/BidPublicInfoService04`
- **인증**: 공공데이터포털 API Key 필요

### 요청 파라미터

| 파라미터명 | 필수 | 설명 | 예시 |
|-----------|:---:|------|------|
| serviceKey | ✅ | 인증키 | - |
| pageNo | | 페이지 번호 | 1 |
| numOfRows | | 페이지당 결과 수 | 100 |
| type | | 응답형식 | json |
| inqryDiv | | 조회구분 (1=공고일, 2=개찰일) | 1 |
| inqryBgnDt | | 조회시작일 | 202412010000 |
| inqryEndDt | | 조회종료일 | 202412182359 |
| bidNtceNm | | 공고명 검색 | 유연탄 |
| dminsttNm | | 수요기관명 | 한국전력공사 |

### 응답 JSON 예시

```json
{
  "response": {
    "header": {
      "resultCode": "00",
      "resultMsg": "정상"
    },
    "body": {
      "numOfRows": 10,
      "pageNo": 1,
      "totalCount": 5,
      "items": {
        "item": [
          {
            "bidNtceNo": "20241256789",
            "bidNtceOrd": "00",
            "bidClsfcNo": "0001",
            "rbidNo": "",
            "ntceDivCd": "1",
            "bidNtceNm": "2024년 하반기 발전용 유연탄 구매",
            "asignBdgtAmt": 50000000000,
            "presmptPrce": 48500000000,
            "bidClseDt": "2024/12/25 17:00",
            "dminsttNm": "한국전력공사",
            "dminsttCd": "1234567890",
            "bidNtceDtlUrl": "https://www.g2b.go.kr/...",
            "rgstDt": "2024/12/10 10:30"
          },
          {
            "bidNtceNo": "20241267890",
            "bidNtceOrd": "00",
            "bidNtceNm": "유연탄(Bituminous Coal) 2025년 1분기 조달",
            "asignBdgtAmt": 35000000000,
            "bidClseDt": "2024/12/28 15:00",
            "dminsttNm": "한국남동발전주식회사",
            "bidNtceDtlUrl": "https://www.g2b.go.kr/..."
          }
        ]
      }
    }
  }
}
```

### 주요 응답 필드 상세

| 필드명 | 타입 | 설명 | 중요도 |
|--------|------|------|:------:|
| **bidNtceNo** | String | 입찰공고번호 (고유키) | ⭐⭐⭐ |
| **bidNtceNm** | String | 입찰공고명 (제목) | ⭐⭐⭐ |
| **bidClseDt** | String | 입찰마감일시 (YYYY/MM/DD HH:MM) | ⭐⭐⭐ |
| **dminsttNm** | String | 수요기관명 (발주처) | ⭐⭐⭐ |
| **asignBdgtAmt** | Number | 배정예산금액 (원) | ⭐⭐ |
| **presmptPrce** | Number | 추정가격 (원) | ⭐⭐ |
| **bidNtceDtlUrl** | String | 상세페이지 URL | ⭐⭐ |
| bidNtceOrd | String | 입찰공고차수 | ⭐ |
| ntceDivCd | String | 공고구분코드 | ⭐ |

---

## 2. 한전SRM (KEPCO) 크롤링 데이터

### 접근 방식
- 공개 공고 목록 페이지 웹 스크래핑
- 로그인 불필요 영역만 대상
- Playwright 브라우저 자동화 사용

### 추출 대상 데이터

| 필드 | HTML 위치 (예상) | 설명 |
|------|-----------------|------|
| 공고번호 | `table td:nth-child(1)` | 고유 식별자 |
| 공고명 | `table td:nth-child(2) a` | 제목 및 상세링크 |
| 분류 | `table td:nth-child(3)` | 물품/공사/용역 |
| 마감일 | `table td:nth-child(4)` | 입찰 마감일시 |
| 첨부파일 | `a[href*=".hwp"]` | HWP 다운로드 링크 |

---

## 3. HWP 파일 파싱 결과

### 추출 대상 스펙 정보

유연탄 입찰 공고 HWP에서 추출해야 할 핵심 스펙:

| 항목 | 검색 패턴 | 예시 값 |
|------|----------|---------|
| 발열량 | `발열량.*(\d{4,5})\s*kcal` | 5,800 kcal/kg |
| 황분 | `황분.*(\d+\.?\d*)\s*%` | 0.8% 이하 |
| 회분 | `회분.*(\d+\.?\d*)\s*%` | 12% 이하 |
| 수분 | `수분.*(\d+\.?\d*)\s*%` | 10% 이하 |
| 물량 | `(\d{1,3}(?:,\d{3})*)\s*(?:MT\|톤)` | 50,000 MT |
| 인코텀즈 | `(FOB\|CIF\|CFR)` | FOB |

### HWP 파싱 결과 JSON 예시

```json
{
  "file_path": "/downloads/공고_20241256789.hwp",
  "is_coal_related": true,
  "keywords_found": ["유연탄", "발열량", "황분", "인도네시아"],
  "coal_spec": {
    "calorific_value_min": 5800,
    "calorific_value_max": null,
    "cv_basis": "NAR",
    "sulfur_max": 0.8,
    "ash_max": 12.0,
    "moisture_max": 10.0,
    "quantity_mt": 50000,
    "origin": "인도네시아",
    "incoterms": "FOB"
  }
}
```

---

## 4. 데이터 흐름도

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  나라장터 API   │     │   한전SRM Web   │     │  발전5사 Web    │
│  (G2B REST)     │     │   (Playwright)  │     │  (Playwright)   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌────────────────────────────────────────────────────────────────┐
│                      G2B/KEPCO Crawler                         │
│                         (Python)                               │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                       HWP Parser                               │
│               (pyhwpx + Regex 패턴 매칭)                        │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                      Gemini AI Filter                          │
│           (관련도 분석, 스펙 검증, 요약 생성)                    │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                      PostgreSQL (Supabase)                     │
│    tenders | tender_specs | tender_attachments | market_data   │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                         n8n Workflow                           │
│              (스케줄링, 알림, 리포트 생성)                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. 발전사 목록 (크롤링 대상)

| 발전사 | 코드 | 입찰사이트 | 비고 |
|--------|------|-----------|------|
| 한국전력공사 | KEPCO | srm.kepco.co.kr | SRM 시스템 |
| 한국남동발전 | KOEN | www.koenergy.kr | |
| 한국중부발전 | KOMIPO | www.komipo.co.kr | |
| 한국서부발전 | KOWEPO | www.iwest.co.kr | |
| 한국남부발전 | KOSPO | www.kospo.co.kr | |
| 한국동서발전 | EWP | www.ewp.co.kr | |

---

## 6. 석탄 스펙 용어 정리

| 용어 | 영문 | 설명 |
|------|------|------|
| 발열량 | Calorific Value (CV) | 석탄 연소 시 발생 열량 (kcal/kg) |
| NAR | Net As Received | 수분 포함 순발열량 (한국 기준) |
| GAR | Gross As Received | 수분 포함 총발열량 (인도네시아 기준) |
| 황분 | Sulfur (S) | 유황 함량 (%), 낮을수록 좋음 |
| 회분 | Ash | 재 함량 (%), 낮을수록 좋음 |
| 수분 | Total Moisture (TM) | 수분 함량 (%) |
| 인코텀즈 | Incoterms | 무역조건 (FOB, CIF 등) |
| Laycan | - | 선적 가능 기간 |
| 체선료 | Demurrage | 선박 지연 시 벌금 |
| 조출료 | Despatch | 조기 하역 시 보너스 |
