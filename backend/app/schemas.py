from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RewriteRequest(BaseModel):
    prompt: str
    style: str = "Ericksonian"
    session_length: int = 10  # in minutes

class RewriteResponse(BaseModel):
    rewritten_script: str
    sections: Optional[List[dict]] = None

class GenerationCreate(BaseModel):
    prompt: str
    custom_script: Optional[str] = None
    style: str
    voice: str
    music_theme: str
    binaural_freq: str
    session_length: int = Field(default=10, ge=1, le=60)
    audio_speed: Optional[float] = 1.0
    audio_pitch: Optional[float] = 1.0
    audio_calmness: Optional[int] = 0
    ambient_volume: Optional[float] = 0.45

class GenerationResponse(BaseModel):
    id: str
    prompt: str
    rewritten_script: Optional[str] = None
    style: str
    voice: str
    music_theme: str
    binaural_freq: str
    session_length: int
    audio_speed: float
    audio_pitch: float
    audio_calmness: int
    ambient_volume: float
    status: str
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    subtitles_url: Optional[str] = None
    error_message: Optional[str] = None
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FavoriteUpdate(BaseModel):
    is_favorite: bool

class PresetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    style: str
    voice: str
    music_theme: str
    binaural_freq: str
    session_length: int

class PresetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    style: str
    voice: str
    music_theme: str
    binaural_freq: str
    session_length: int
    created_at: datetime

    class Config:
        from_attributes = True
