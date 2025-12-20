# CarbonFlow Intelligence System - PRD

## 1. 개요 (Overview)
- **제품명:** CarbonFlow Intelligence System (CIS)
- **버전:** 1.0 (MVP)
- **목적:** 국내 주요 발전사 및 공공기관의 연료(유연탄) 입찰 정보를 실시간으로 수집, 분석하고, 선박 물류 및 정산 업무를 자동화하여 트레이딩 팀의 의사결정 속도와 정확성을 제고함.
- **타겟 사용자:** KCH 그룹 사원사업본부 트레이더 및 운영 담당자.

---

## 2. 개발 페르소나 정의

### 페르소나 A: 알고리즘 PM (The Algorithmic Architect)
- **역할:** 시스템의 '두뇌' 설계. 비즈니스 로직 정의 및 데이터 흐름 설계
- **핵심 과업:** GAR/NAR 변환, Incoterms(FOB, CIF) 정산 로직, 체선료(Demurrage) 판단 알고리즘
- **산출물:** PRD, ERD, API 명세서

### 페르소나 B: 자동화 엔지니어 (The N8N Specialist)
- **역할:** 설계된 로직을 파이프라인으로 구현. '연결'에 집중
- **핵심 과업:** n8n 워크플로우 구축, 이메일 선적서류 자동분류, 환율/석탄가격 API 연동
- **산출물:** n8n Workflow JSON, 커스텀 노드 스크립트

### 페르소나 C: 포렌식 데이터 엔지니어 (The Crawler)
- **역할:** 폐쇄형 입찰 사이트에서 데이터 채굴
- **핵심 과업:** KEPCO SRM/나라장터 스크래핑, HWP 파싱, 스펙 데이터 추출
- **산출물:** Python/Playwright 스크립트, HWP 파싱 라이브러리

---

## 3. 핵심 기능 요구사항

### Epic 1: 지능형 입찰 정보 수집기
- **FR-1.1:** Multi-Source Crawling (KEPCO SRM, G2B, 발전5사)
- **FR-1.2:** HWP Deep Parsing (발열량, 황분, 낙찰자 결정 방법 추출)
- **FR-1.3:** AI 필터링 (Gemini로 관련도 점수 부여, 80%↑ 시 Slack 알림)

### Epic 2: 선박 및 물류 관제
- **FR-2.1:** SOF Digitization (OCR로 접안/하역 시간 추출)
- **FR-2.2:** Laytime Calculator (체선료/조출료 자동 계산)
- **FR-2.3:** Vessel Tracking (MMSI 기반 실시간 위치, ETA 지연 경고)

### Epic 3: 트레이딩 데이터 허브
- **FR-3.1:** Market Index Integration (Global Coal, Argus 가격 수집)
- **FR-3.2:** Netback Calculator (마진 시뮬레이션 대시보드)

---

## 4. 기술 스택
| 구분 | 기술 |
|------|------|
| 오케스트레이션 | n8n (Self-Hosted) |
| 데이터베이스 | Supabase (PostgreSQL + pgvector) |
| 크롤링 | Python + Playwright |
| AI | Gemini API |
| 컨테이너 | OrbStack |
| IDE | Google Antigravity |

---

## 5. 비기능 요구사항
- **보안:** 계정 정보는 환경변수로 관리
- **안정성:** 요청 간격 무작위화, User-Agent 로테이션
- **가용성:** 24/7 가동, 장애 시 10분 이내 알림
