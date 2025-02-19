from pydantic import BaseModel
from typing import Optional

class AttachmentData(BaseModel):
    type: str
    data: list

class Attachment(BaseModel):
    dataBuffer: AttachmentData
    mimetype: str = "application/pdf;base64"
    extension: str = "pdf"

class ScheduledPlan(BaseModel):
    title: str
    url: str
    scheduledPlanId: str
    type: str

class FormParams(BaseModel):
    google_chat_webhook: Optional[str] = None
    slack_webhook: Optional[str] = None
    teams_webhook: Optional[str] = None
    prompt_selection: str # A prompt needs to be selected

class DashboardWebhook(BaseModel):
    attachment: Attachment
    scheduled_plan: ScheduledPlan
    form_params: FormParams
    type: str = "dashboard"

class SummaryResponseSchemaProperties(BaseModel):
    title: dict = {"type": "string"}
    description: dict = {"type": "string"}
    summary: dict = {"type": "string"}
    next_steps: dict = {"type": "string"}

class SummaryResponseSchema(BaseModel):
    type: str = "object"
    properties: SummaryResponseSchemaProperties = SummaryResponseSchemaProperties()
    required: list = ["title", "description", "summary", "next_steps"]