from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    TIMESTAMP,
    SmallInteger,
    DECIMAL,
    TEXT,
    Float,
    JSON,
    BigInteger
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
    created_at = Column(TIMESTAMP, server_default=func.now())
    expired_at = Column(TIMESTAMP, nullable=True)
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

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    main_category = Column(String(10), nullable=False)
    sub_category = Column(String(10), nullable=False)
    content = Column(String(50), nullable=False)
    input_type = Column(Enum(TypeEnum), nullable=False)
    icon_path = Column(String(100))
    code = Column(SmallInteger, nullable=False)
    state = Column(Enum(StateEnum), server_default=expression.text("'active'"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    expired_at = Column(TIMESTAMP, nullable=True)
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

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    homie_question_id = Column(
        SmallInteger, ForeignKey("Homie_questions.id"), nullable=False
    )
    content = Column(String(50), nullable=False)
    score = Column(SmallInteger, nullable=True)
    state = Column(Enum(StateEnum), server_default=expression.text("'active'"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    expired_at = Column(TIMESTAMP, nullable=True)
    homie_question = relationship("HomieQuestion", back_populates="homie_answers")

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
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user = relationship("User", back_populates="homie_histories")
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
    homie_history_id = Column(Integer, ForeignKey("Homie_histories.id"), nullable=False)
    homie_question_id = Column(
        SmallInteger, ForeignKey("Homie_questions.id"), nullable=False
    )
    homie_answer_id = Column(
        SmallInteger, ForeignKey("Homie_answers.id"), nullable=False
    )
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


class HomieDong(Base):
    __tablename__ = "Homie_dongs"
    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    district = Column(String(4), nullable=False)
    dong = Column(String(6), nullable=False)
    homie_dong_coefficients = relationship(
        "HomieDongCoefficient", back_populates="homie_dong"
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


class HomieDongCoefficient(Base):
    __tablename__ = "Homie_dong_coefficients"
    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    homie_dong_id = Column(SmallInteger, ForeignKey("Homie_dongs.id"), nullable=False)
    sub_category = Column(String(10), nullable=False)
    coefficient = Column(DECIMAL(6, 5), nullable=False)
    homie_dong = relationship("HomieDong", back_populates="homie_dong_coefficients")

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


class SeoulDongCode(Base):
    __tablename__ = "Seoul_dong_codes"

    code = Column(String(20), primary_key=True)
    full_name = Column(String(50), nullable=False)
    gu_name = Column(String(10), nullable=False)
    dong_name = Column(String(10), nullable=False)
    short_code = Column(String(10), nullable=False)

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


class SeoulRoom(Base):
    __tablename__ = "Seoul_rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dong_code = Column(String(20))
    gu_name = Column(String(20))
    dong_name = Column(String(20))
    seq = Column(Integer)
    room_type = Column(String(50))
    room_title = Column(String(255))
    room_desc = Column(TEXT)
    price_type = Column(String(20))
    price_info = Column(String(50))
    img_url_list = Column(JSON)
    lat = Column(Float)
    lng = Column(Float)
    floor = Column(String(20))
    area_m2 = Column(Float)
    deposit = Column(BigInteger)
    monthly = Column(Integer)
    maintenance_fee = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


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


class SubwayStation(Base):
    __tablename__ = "Subway_stations"
    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)

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
