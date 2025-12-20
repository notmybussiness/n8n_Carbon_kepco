# Project Progress

## ✅ Completed
- [x] Docker environment setup (OrbStack)
- [x] n8n workflow engine running
- [x] PostgreSQL + PostgREST configured
- [x] Parser Provider pattern implemented
- [x] **KEPCO Crawler V3** - stable selectors, retry logic, logging

## 🔄 In Progress
- [ ] KEPCO crawler improvement
  - Basic structure in `crawlers/kepco/crawler.py`
  - Needs: Better parsing, error handling, data extraction

## 📋 TODO
- [ ] Parser output format selection
- [ ] Dashboard implementation
- [ ] n8n workflow automation
- [x] **Supabase integration** (Schema applied, Repository implemented)
- [x] **Crawler-DB Integration** (KEPCO crawler connected to Supabase)

## 🔄 In Progress
- [ ] KEPCO crawler improvement
  - Basic structure in `crawlers/kepco/crawler.py`
  - Needs: Stable selectors, Timeout handling
- [ ] Dashboard implementation
- [ ] n8n workflow automation
- [ ] Parser output format selection
```
workflow_n8n/
├── crawlers/
│   ├── main.py          # FastAPI entrypoint
│   ├── kepco/           # KEPCO SRM crawler
│   ├── parsers/         # Document parsers
│   └── dto.py           # Data models
├── docs/                # Documentation
├── n8n/                 # Workflow configs
├── supabase/            # DB migrations
└── docker-compose.yml
```
