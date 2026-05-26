import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Generation(Base):
    __tablename__ = "generations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    prompt = Column(Text, nullable=False)
    rewritten_script = Column(Text, nullable=True)
    style = Column(String(50), nullable=False)
    voice = Column(String(50), nullable=False)
    music_theme = Column(String(50), nullable=False)
    binaural_freq = Column(String(50), nullable=False)
    session_length = Column(Integer, nullable=False)  # in minutes
    
    # Audio customization controls
    audio_speed = Column(Float, default=1.0)
    audio_pitch = Column(Float, default=1.0)
    audio_calmness = Column(Integer, default=0)
    ambient_volume = Column(Float, default=0.45)
    
    status = Column(String(30), default="pending")  # pending, rewriting, synthesizing, layering, video, completed, failed
    audio_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    subtitles_url = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Preset(Base):
    __tablename__ = "presets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    style = Column(String(50), nullable=False)
    voice = Column(String(50), nullable=False)
    music_theme = Column(String(50), nullable=False)
    binaural_freq = Column(String(50), nullable=False)
    session_length = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
