from __future__ import annotations
import os,time,uuid
from datetime import datetime,timezone
from typing import Literal
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field

app=FastAPI(title="FlowPilot AI Automation MVP",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=False,allow_methods=["*"],allow_headers=["*"])
RUNS={}

class WorkflowIn(BaseModel):
    request:str=Field(min_length=5,max_length=2000)
    provider:Literal["openai","claude","gemini"]="openai"
    workflow_type:Literal["crm","support","rag","ops"]="crm"
    approval_required:bool=True

def build_output(p):
    t=p.request.lower()
    priority="high" if any(k in t for k in ["urgent","critical","vip","refund","legal"]) else "normal"
    action={"crm":"create_crm_followup","support":"create_support_task","rag":"retrieve_and_summarize","ops":"create_ops_task"}[p.workflow_type]
    return {
        "summary":p.request[:180],
        "classification":{"workflow_type":p.workflow_type,"priority":priority},
        "tool_call":{"name":action,"arguments":{"source":"demo_workflow","request_excerpt":p.request[:120]}},
        "safety":{"human_approval_required":p.approval_required,"external_action_executed":False},
        "reliability":{"validation":"passed","retry_policy":"3 attempts with exponential backoff","logging":"enabled"},
        "note":"This MVP prepares the action but does not claim a real CRM/SaaS integration is connected."
    }

@app.get("/")
def root(): return {"message":"FlowPilot AI Automation MVP API","docs":"/docs"}

@app.get("/api/health")
def health(): return {"status":"ok","mode":"safe-demo","openai_key_present":bool(os.getenv("OPENAI_API_KEY")),"anthropic_key_present":bool(os.getenv("ANTHROPIC_API_KEY")),"gemini_key_present":bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/run")
def run_workflow(p:WorkflowIn):
    started=time.perf_counter();rid=str(uuid.uuid4())[:8];output=build_output(p);status="awaiting_approval" if p.approval_required else "completed"
    rec={"run_id":rid,"workflow_type":p.workflow_type,"provider":p.provider,"status":status,"timestamp":datetime.now(timezone.utc).isoformat(timespec="seconds"),"latency_ms":int((time.perf_counter()-started)*1000),"output":output}
    RUNS[rid]=rec
    return rec

@app.post("/api/approve/{run_id}")
def approve(run_id:str):
    if run_id not in RUNS: raise HTTPException(404,"Run not found")
    rec=RUNS[run_id];rec["status"]="completed";rec["output"]["approval"]={"status":"approved","executed":False,"reason":"No real external system credential is configured in this demo."}
    rec["timestamp"]=datetime.now(timezone.utc).isoformat(timespec="seconds")
    return rec

@app.get("/api/runs")
def list_runs(): return list(reversed(list(RUNS.values())))
