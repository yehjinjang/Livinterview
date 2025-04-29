from fastapi import APIRouter
from pydantic import BaseModel
from chatbot_core.utils import gpt
from chatbot_core.prompts import (
    question_check_prompt,
    check_partial_agreement_prompt,
    extract_proposal_prompt,
    summary_prompt,
    check_completion_prompt,
    followup_question_prompt,
    furniture_warning_prompt,
    controlnet_prompt,
    check_prompt
)

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str
    gpt_response: str = None  # 일부는 gpt_response 필요

class ConversationRequest(BaseModel):
    conversation: str

class SummaryRequest(BaseModel):
    conversation: str

class ControlNetRequest(BaseModel):
    summary: str

@router.post("/question")
async def analyze_question(req: AnalyzeRequest):
    prompt = question_check_prompt.format(text=req.text)
    return {"result": gpt.invoke(prompt).content}

@router.post("/agreement")
async def analyze_agreement(req: AnalyzeRequest):
    prompt = check_partial_agreement_prompt.format(gpt_response=req.gpt_response, text=req.text)
    return {"result": gpt.invoke(prompt).content}

@router.post("/extract")
async def analyze_extract(req: AnalyzeRequest):
    prompt = extract_proposal_prompt.format(response=req.text)
    return {"result": gpt.invoke(prompt).content}

@router.post("/summary")
async def analyze_summary(req: SummaryRequest):
    prompt = summary_prompt.format(conversation=req.conversation)
    return {"result": gpt.invoke(prompt).content}

@router.post("/check-completion")
async def analyze_check_completion(req: AnalyzeRequest):
    prompt = check_completion_prompt.format(text=req.text)
    return {"result": gpt.invoke(prompt).content}

@router.post("/followup")
async def analyze_followup(req: ConversationRequest):
    prompt = followup_question_prompt.format(conversation=req.conversation)
    return {"result": gpt.invoke(prompt).content}

@router.post("/furniture-warning")
async def analyze_furniture_warning(req: ConversationRequest):
    prompt = furniture_warning_prompt.format(conversation=req.conversation)
    return {"result": gpt.invoke(prompt).content}

@router.post("/controlnet")
async def analyze_controlnet(req: ControlNetRequest):
    prompt = controlnet_prompt.format(summary=req.summary)
    return {"result": gpt.invoke(prompt).content}
