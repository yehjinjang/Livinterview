from fastapi import Depends, APIRouter
from database import get_db
from sqlalchemy.orm import Session
from models import (
    GenderEnum,
    StateEnum,
    TypeEnum,
    User,
    HomieQuestion,
    HomieAnswer,
    HomieHistory,
    HomieQnAHistory,
    HomieDong,
    HomieDongCoefficient,
    SeoulDongCode,
    SeoulRoom,
    SubwayStation,
)

router = APIRouter()


@router.get("/qna")
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(HomieQuestion).order_by(HomieQuestion.code.asc()).all()
    qna_list = []
    for question in questions:
        question_data = question.to_dict()
        question_data["answers"] = [
            answer.to_dict() for answer in question.homie_answers
        ]
        qna_list.append(question_data)
    return qna_list
