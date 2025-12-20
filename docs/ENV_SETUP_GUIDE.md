# CarbonFlow .env 설정 가이드

## 필수 API 키

### 1. 공공데이터포털 API (DATA_GO_KR_API_KEY)
**용도**: 나라장터 입찰공고 조회 (G2B API)

**발급 방법**:
1. https://www.data.go.kr 접속
2. 회원가입 후 로그인
3. 검색창에 "나라장터 입찰공고정보서비스" 검색
4. 해당 API 클릭 → "활용신청" 버튼
5. 신청 목적 작성 (예: "입찰 정보 모니터링 시스템 개발")
6. 승인 후 마이페이지에서 "인증키" 복사

**특징**:
- 무료
- 일 1,000회 호출 가능 (상향 신청 가능)
- 승인까지 약 1~2시간 소요

---

### 2. Gemini API (GEMINI_API_KEY)
**용도**: HWP 문서 분석, 입찰 관련도 판단, AI 요약 생성

**발급 방법**:
1. https://aistudio.google.com 접속
2. Google 계정 로그인
3. 좌측 메뉴 "Get API key" 클릭
4. "Create API key" 버튼 클릭
5. 키 복사

**특징**:
- 무료 티어 제공 (분당 60회)
- Pro 버전은 유료

---

## 선택적 API 키

### 3. MarineTraffic API (MARINE_TRAFFIC_API_KEY)
**용도**: 선박 실시간 위치 추적, ETA 조회

**발급 방법**:
1. https://www.marinetraffic.com/en/ais-api-services 접속
2. 회원가입
3. API 플랜 선택 (유료)
4. Basic 플랜: 월 $20~

**대안**: 
- VesselFinder API (https://www.vesselfinder.com/api)
- 무료 데모 계정으로 테스트 가능

---

## .env 파일 예시

```env
# ===== PostgreSQL Database =====
POSTGRES_USER=carbonflow
POSTGRES_PASSWORD=carbonflow2024

# ===== n8n Workflow =====
N8N_USER=admin
N8N_PASSWORD=carbonflow2024

# ===== PostgREST API =====
JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters

# ===== 공공데이터포털 API (필수) =====
DATA_GO_KR_API_KEY=발급받은_인증키_여기에_붙여넣기

# ===== Gemini API (선택) =====
GEMINI_API_KEY=발급받은_API_키

# ===== MarineTraffic API (선택) =====
MARINE_TRAFFIC_API_KEY=
```

---

## 우선순위

| 순번 | API | 중요도 | 비용 | 용도 |
|:---:|-----|:------:|:----:|------|
| 1 | DATA_GO_KR_API_KEY | ⭐⭐⭐ | 무료 | 입찰공고 수집 (핵심) |
| 2 | GEMINI_API_KEY | ⭐⭐ | 무료 | AI 분석/요약 |
| 3 | MARINE_TRAFFIC_API_KEY | ⭐ | 유료 | 선박 추적 (나중에) |

**👉 우선 1번(공공데이터포털)만 발급받으시면 입찰 수집 테스트 가능합니다!**
