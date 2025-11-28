from sqlalchemy import (
    Column, Integer, BigInteger, String, Float, Text,
    TIMESTAMP, ForeignKey, Boolean
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func
from app.config.database import Base


class EmotionClass(Base):
    __tablename__ = "emotion_class"
    emotion_id = Column(Integer, primary_key=True, autoincrement=True)
    emotion_name = Column(String(50), unique=True, nullable=False)
    emotion_desc = Column(Text, nullable=True)

class ModelVersion(Base):
    __tablename__ = "model_version"
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_version_tag = Column(String(100), unique=True, nullable=False)
    model_filename = Column(String(255), nullable=False)
    model_status = Column(String(2), nullable=False)
    creation_date = Column(TIMESTAMP(timezone=True), server_default=func.now())

class PredictionsLog(Base):
    __tablename__ = "predictions_log"
    predic_id = Column(BigInteger, primary_key=True, autoincrement=True)
    emotion_id = Column(Integer, ForeignKey("emotion_class.emotion_id"), nullable=False)
    confidence = Column(Float, nullable=False)
    model_id = Column(Integer, ForeignKey("model_version.model_id"), nullable=False)
    processing_time_ms = Column(Integer)
    source_ip = Column(INET)
    user = Column(String(50), nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
