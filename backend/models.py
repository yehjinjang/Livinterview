from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    TIMESTAMP,
    SmallInteger,
    DATE,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func, expression
import enum

Base = declarative_base()


class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    unspecified = "unspecified"


class StateEnum(enum.Enum):
    active = "active"
    inactive = "inactive"


class TypeEnum(enum.Enum):
    select = "select"
    radio = "radio"
    text = "text"


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(11))
    birth = Column(DATE)
    gender = Column(Enum(GenderEnum), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    modified_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    expired_at = Column(TIMESTAMP)
    state = Column(Enum(StateEnum), server_default=expression.text("'active'"))
    homie_histories = relationship("HomieHistory", back_populates="user")

    def __repr__(self):
        cols = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            cols.append(f"{column.name}={value}")
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            data[column.name] = value
        return data


class HomieQuestion(Base):
    __tablename__ = "Homie_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    main_category = Column(String(10), nullable=False)
    sub_category = Column(String(10), nullable=False)
    content = Column(String(50), nullable=False)
    input_type = Column(Enum(TypeEnum), nullable=False)
    icon_path = Column(String(100))
    state = Column(Enum(StateEnum), server_default=expression.text("'active'"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    expired_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    homie_answers = relationship("HomieAnswer", back_populates="homie_question")

    def __repr__(self):
        cols = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            cols.append(f"{column.name}={value}")
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            data[column.name] = value
        return data


class HomieAnswer(Base):
    __tablename__ = "Homie_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    homie_questions_id = Column(
        Integer, ForeignKey("Homie_questions.id"), nullable=False
    )
    content = Column(String(50), nullable=False)
    score = Column(SmallInteger, nullable=False)
    state = Column(Enum(StateEnum), server_default=expression.text("'active'"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    expired_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    homie_question = relationship("HomieAnswer", back_populates="homie_answers")

    def __repr__(self):
        cols = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            cols.append(f"{column.name}={value}")
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, enum.Enum):
                value = value.value
            data[column.name] = value
        return data


class HomieHistory(Base):
    __tablename__ = "Homie_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_id = relationship("User", back_populates="homie_histories")
    homie_qna_histories = relationship(
        "HomieQnAHistory", back_populates="homie_history"
    )

    def __repr__(self):
        cols = [
            f"{column.name}={getattr(self, column.name)}"
            for column in self.__table__.columns
        ]
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class HomieQnAHistory(Base):
    __tablename__ = "Homie_qna_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    homie_histories_id = Column(
        Integer, ForeignKey("Homie_histories.id"), nullable=False
    )
    homie_questions_id = Column(
        Integer, ForeignKey("Homie_questions.id"), nullable=False
    )
    homie_answers_id = Column(Integer, ForeignKey("Homie_answers.id"), nullable=False)
    homie_history = relationship("HomieHistory", back_populates="homie_qna_histories")

    def __repr__(self):
        cols = [
            f"{column.name}={getattr(self, column.name)}"
            for column in self.__table__.columns
        ]
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
