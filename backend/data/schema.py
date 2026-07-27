"""
Single source of truth for the incident data shape.
Every generated document (postmortem, runbook, slack-thread) must
ultimately produce an Incident object that validates against this.
"""
from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


Severity = Literal["SEV1", "SEV2", "SEV3", "SEV4"]
DocType = Literal["postmortem", "runbook", "slack_thread", "github_issue", "raw_log"]


class Incident(BaseModel):
    incident_id: str                     # e.g. "INC-0001"
    service: str                         # e.g. "checkout-service"
    severity: Severity
    symptom_description: str             # the "query-shaped" text, e.g. how an engineer would describe it live
    root_cause: str                      # e.g. "db_connection_pool_exhaustion" — used to group incident families
    resolution_steps: list[str]
    timestamp: datetime
    deploy_version: Optional[str] = None
    related_incident_ids: list[str] = Field(default_factory=list)

    doc_type: DocType
    doc_text: str                        # the actual generated document body (postmortem/runbook/thread text)

    is_distractor: bool = False          # superficially similar wording, different root cause — for rerank testing
    is_novel: bool = False               # the one incident with no family — for guardrail testing


class DeployEvent(BaseModel):
    service: str
    version: str
    timestamp: datetime
    commit_message: str
