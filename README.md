# 🔥 CarbonFlow Intelligence

실시간 석탄 입찰 공고 자동 수집 및 분석 시스템

---

## 📸 스크린샷

### Dashboard

> 단순 데이터 수집을 넘어, **유연탄 지수(ICI4, Newcastle)와 선박 입항 예정일(ETA)을 한눈에 파악**할 수 있도록 시각화한 대시보드입니다.

![Dashboard](docs/images/dashboard.png)

### n8n Workflow Automation

> KEPCO 입찰 사이트 조회 → 신규 공고 확인 → **Google Sheets 자동 저장** → **Slack/Email 알림**까지 전 과정 자동화

![n8n Workflow](docs/images/n8n_workflow.png)

### Supabase 저장 데이터 샘플

| 공고번호            | 공고명                 | 발주기관         | 상태 |
| ------------------- | ---------------------- | ---------------- | ---- |
| SIM-TEST-1766233857 | Simulation Test Tender | -                | OPEN |
| 20241220001         | Test Coal Tender 2024  | Korea Test Power | OPEN |

---

## ⚡ 업무 효율화 효과

### Before (기존 방식)

| 단계 | 업무 내용                   | 소요 시간   | 문제점         |
| ---- | --------------------------- | ----------- | -------------- |
| 1    | 출근 후 KEPCO SRM 포털 접속 | 5분         | 매일 수동 접속 |
| 2    | 발전사별 입찰 공고 검색     | 20분        | 누락 가능성    |
| 3    | 엑셀에 수기로 정리          | 10분        | 오타 발생 위험 |
| 4    | 팀원들에게 카톡/메일 공유   | 5분         | 알림 지연      |
|      | **합계**                    | **40분/일** |                |

### After (CarbonFlow 방식)

| 단계 | 자동화 내용                    | 소요 시간  | 개선 효과    |
| ---- | ------------------------------ | ---------- | ------------ |
| 1    | n8n 봇이 08:30에 자동 크롤링   | 0분        | 출근 전 완료 |
| 2    | 조건 분기로 신규 공고만 필터링 | 0분        | 100% 정확도  |
| 3    | Google Sheets 자동 저장        | 0분        | 오타 없음    |
| 4    | Slack/Email 자동 알림          | 0분        | 실시간 공유  |
|      | **합계**                       | **0분/일** | **95% 단축** |

---

## ✨ 주요 기능

### 1. 🤖 자동 크롤링

- KEPCO SRM 포털에서 석탄 입찰 공고 자동 수집
- Playwright 기반 동적 웹 크롤링
- n8n 스케줄러로 **매일 08:30** 자동 실행

### 2. 📄 HWP 문서 파싱

- 한글 파일(.hwp)에서 석탄 규격 자동 추출
- 발열량(GCV), 유황분, 회분, 수분 등 핵심 스펙 파싱

### 3. 📊 실시간 대시보드

- Glassmorphism 다크 테마 UI
- Supabase 실시간 연동
- **ICI4, Newcastle 유연탄 지수** 실시간 표시
- **선박 ETA, 입찰 현황** KPI 카드

### 4. 🔔 스마트 알림

- 신규 공고 발생 시 **Slack 채널 알림**
- **이메일 자동 발송** (담당자 직접 수신)
- Google Sheets 연동으로 **이력 자동 관리**

### 5. 💾 데이터 파이프라인

- Supabase PostgreSQL 클라우드 저장
- Docker Compose 기반 서비스 오케스트레이션

---

## 🛠 기술 스택

| 분류        | 기술                             |
| ----------- | -------------------------------- |
| Backend     | Python 3.12, FastAPI, Playwright |
| Database    | Supabase (PostgreSQL)            |
| Frontend    | Next.js 15, Tailwind CSS v4      |
| Automation  | **n8n**, Docker                  |
| Integration | Google Sheets, Slack, SMTP       |

---

## 🔄 n8n 워크플로우 상세

```
⏰ 매일 08:30 실행
       │
       ▼
🔍 KEPCO SRM 조회 (HTTP Request)
       │
       ▼
❓ 신규 공고 확인 (If 조건분기)
       │
   ┌───┴───┐
   │       │
   ▼       ▼
📊 Google  ✅ 완료
   Sheets  (변경 없음)
   저장
   │
   ├───────┐
   ▼       ▼
💬 Slack  📧 Email
   알림     발송
```

---

## 🚀 실행 방법

### 1. 환경 설정

```bash
cp .env.example .env
# .env 파일에 Supabase 키 입력
```

### 2. Docker로 실행

```bash
docker-compose up -d
```

### 3. 대시보드 실행

```bash
cd dashboard
npm install
npm run dev
```

### 4. 접속

- **n8n**: http://localhost:5678
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000

---

## 📂 프로젝트 구조

```
├── crawlers/           # Python 크롤러
│   ├── kepco/          # KEPCO 전용 크롤러
│   ├── repository.py   # Supabase 연동
│   └── main.py         # FastAPI 서버
├── dashboard/          # Next.js 대시보드
├── n8n/                # 워크플로우 설정
│   └── kepco_workflow.json  # 입찰공고 자동화 워크플로우
├── supabase/           # DB 마이그레이션
└── docker-compose.yml
```

---

## 📊 데이터 모델

- `tenders` - 입찰 공고
- `tender_attachments` - 첨부파일
- `tender_specs` - 석탄 규격
- `market_data` - 시장 지수 (ICI4, Newcastle)
- `shipments` - 선적 정보

---

## 📝 License

MIT
