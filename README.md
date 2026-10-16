# FlowPilot AI - Quick MVP

Tailored to an AI Automation Developer / AI Agent / LLM Integration / Workflow Automation Upwork role.

## Working features
- Responsive AI automation dashboard
- Business-request workflow runner
- OpenAI / Claude / Gemini provider selection
- CRM / Support / RAG / Operations workflow modes
- Structured tool-call style output
- Human-in-the-loop approval gate
- Execution log
- Retry/logging metadata
- FastAPI backend
- Automated API tests

## Run backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run frontend
```bash
cd frontend
python -m http.server 5500
```
Open http://127.0.0.1:5500

## Credentials for live integrations
Optional next-step credentials:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GEMINI_API_KEY
- N8N_WEBHOOK_URL
- CRM_API_URL
- CRM_API_KEY

This MVP does not pretend a real CRM, n8n flow, or LLM provider is already connected.
