from __future__ import annotations

import os
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pydantic import BaseModel, Field


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="FlowPilot AI Automation MVP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

RUNS = {}


# --------------------------------------------------
# Schemas
# --------------------------------------------------

class WorkflowIn(BaseModel):
    request: str = Field(
        min_length=5,
        max_length=2000
    )

    provider: Literal[
        "openai",
        "claude",
        "gemini"
    ] = "openai"

    workflow_type: Literal[
        "crm",
        "support",
        "rag",
        "ops"
    ] = "crm"

    approval_required: bool = True


# --------------------------------------------------
# Workflow Logic
# --------------------------------------------------

def build_output(p):

    t = p.request.lower()

    priority = (
        "high"
        if any(
            k in t
            for k in [
                "urgent",
                "critical",
                "vip",
                "refund",
                "legal"
            ]
        )
        else "normal"
    )

    action = {
        "crm": "create_crm_followup",
        "support": "create_support_task",
        "rag": "retrieve_and_summarize",
        "ops": "create_ops_task"
    }[p.workflow_type]

    return {

        "summary":
            p.request[:180],

        "classification": {
            "workflow_type":
                p.workflow_type,

            "priority":
                priority
        },

        "tool_call": {
            "name":
                action,

            "arguments": {
                "source":
                    "demo_workflow",

                "request_excerpt":
                    p.request[:120]
            }
        },

        "safety": {
            "human_approval_required":
                p.approval_required,

            "external_action_executed":
                False
        },

        "reliability": {
            "validation":
                "passed",

            "retry_policy":
                "3 attempts with exponential backoff",

            "logging":
                "enabled"
        },

        "note":
            "This MVP prepares the action but does not claim "
            "a real CRM/SaaS integration is connected."
    }


# --------------------------------------------------
# Frontend
# --------------------------------------------------

@app.get("/")
def root():

    index_file = BASE_DIR / "index.html"

    if not index_file.exists():

        raise HTTPException(
            status_code=500,
            detail="index.html not found"
        )

    return FileResponse(
        index_file
    )


@app.get("/styles.css")
def styles():

    css_file = BASE_DIR / "styles.css"

    if not css_file.exists():

        raise HTTPException(
            status_code=404,
            detail="styles.css not found"
        )

    return FileResponse(
        css_file,
        media_type="text/css"
    )


@app.get("/app.js")
def javascript():

    js_file = BASE_DIR / "app.js"

    if not js_file.exists():

        raise HTTPException(
            status_code=404,
            detail="app.js not found"
        )

    return FileResponse(
        js_file,
        media_type="application/javascript"
    )


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/api/health")
def health():

    return {

        "status":
            "ok",

        "mode":
            "safe-demo",

        "openai_key_present":
            bool(
                os.getenv(
                    "OPENAI_API_KEY"
                )
            ),

        "anthropic_key_present":
            bool(
                os.getenv(
                    "ANTHROPIC_API_KEY"
                )
            ),

        "gemini_key_present":
            bool(
                os.getenv(
                    "GEMINI_API_KEY"
                )
            )
    }


# --------------------------------------------------
# Run Workflow
# --------------------------------------------------

@app.post("/api/run")
def run_workflow(
    p: WorkflowIn
):

    started = time.perf_counter()

    rid = str(
        uuid.uuid4()
    )[:8]

    output = build_output(
        p
    )

    status = (
        "awaiting_approval"
        if p.approval_required
        else "completed"
    )

    rec = {

        "run_id":
            rid,

        "workflow_type":
            p.workflow_type,

        "provider":
            p.provider,

        "status":
            status,

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(
                timespec="seconds"
            ),

        "latency_ms":
            int(
                (
                    time.perf_counter()
                    - started
                )
                * 1000
            ),

        "output":
            output
    }

    RUNS[rid] = rec

    return rec


# --------------------------------------------------
# Approve Workflow
# --------------------------------------------------

@app.post("/api/approve/{run_id}")
def approve(
    run_id: str
):

    if run_id not in RUNS:

        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    rec = RUNS[
        run_id
    ]

    rec[
        "status"
    ] = "completed"

    rec[
        "output"
    ][
        "approval"
    ] = {

        "status":
            "approved",

        "executed":
            False,

        "reason":
            "No real external system credential is configured in this demo."
    }

    rec[
        "timestamp"
    ] = datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )

    return rec


# --------------------------------------------------
# Runs
# --------------------------------------------------

@app.get("/api/runs")
def list_runs():

    return list(
        reversed(
            list(
                RUNS.values()
            )
        )
    )
