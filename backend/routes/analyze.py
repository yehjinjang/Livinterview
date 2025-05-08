# backend/routes/analyze.py
from fastapi import APIRouter
from pydantic import BaseModel
from chatbot_core.memory.session_memory import memory
from chatbot_core.chains import (
    question_check_chain,
    check_agreement_chain,
    extract_proposal_chain,
    summary_chain,
    check_completion_chain,
    followup_chain,
    furniture_warning_chain,
    controlnet_chain
)

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str
    gpt_response: str | None = None

class ConversationRequest(BaseModel):
    conversation: str

class ControlNetRequest(BaseModel):
    summary: str

@router.post("/question")
async def analyze_question(req: AnalyzeRequest):
    return {"result": question_check_chain.run({"text": req.text})}

@router.post("/agreement")
async def analyze_agreement(req: AnalyzeRequest):
    return {"result": check_agreement_chain.run({"gpt_response": req.gpt_response, "text": req.text})}

@router.post("/extract")
async def analyze_extract(req: AnalyzeRequest):
    return {"result": extract_proposal_chain.run({"response": req.text})}

@router.post("/summary")
async def analyze_summary(req: ConversationRequest):
    return {"result": summary_chain.run({"conversation": req.conversation})}

@router.post("/check-completion")
async def analyze_check_completion(req: AnalyzeRequest):
    return {"result": check_completion_chain.run({"text": req.text})}

@router.post("/followup")
async def analyze_followup(req: ConversationRequest):
    return {"result": followup_chain.run({"conversation": req.conversation})}

@router.post("/furniture-warning")
async def analyze_furniture_warning(req: ConversationRequest):
    return {"result": furniture_warning_chain.run({"conversation": req.conversation})}

@router.post("/controlnet")
async def analyze_controlnet(req: ControlNetRequest):
    return {"result": controlnet_chain.run({"summary": req.summary})}

@router.post("/summarize-memory")
async def summarize_from_memory():
    from chatbot_core.memory.session_memory import memory

    # 사용자 타입 메시지 기준으로 체크
    user_messages = [
        m.content for m in memory.chat_memory.messages if m.type == "human"
    ]
    if not user_messages:
        return {"result": "요약할 대화가 없습니다."}

    history = memory.load_memory_variables({})["chat_history"]
    summary = summary_chain.run({"conversation": history})
    memory.chat_memory.add_ai_message(summary)
    memory.chat_memory.add_ai_message("SUMMARY_PENDING_CONFIRMATION")
    return {"result": summary}