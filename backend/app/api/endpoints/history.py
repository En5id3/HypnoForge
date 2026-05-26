from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models import Generation, Preset
from backend.app.schemas import GenerationResponse, FavoriteUpdate, PresetCreate, PresetResponse

router = APIRouter()

# --- Generation History ---

@router.get("/generations", response_model=List[GenerationResponse])
def list_generations(db: Session = Depends(get_db)):
    """
    Returns list of all session generations ordered by newest first.
    """
    return db.query(Generation).order_by(Generation.created_at.desc()).all()

@router.get("/generations/{gen_id}", response_model=GenerationResponse)
def get_generation(gen_id: str, db: Session = Depends(get_db)):
    gen = db.query(Generation).filter(Generation.id == gen_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return gen

@router.put("/generations/{gen_id}/favorite", response_model=GenerationResponse)
def toggle_favorite(gen_id: str, payload: FavoriteUpdate, db: Session = Depends(get_db)):
    """
    Mark/unmark a session as a favorite.
    """
    gen = db.query(Generation).filter(Generation.id == gen_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    gen.is_favorite = payload.is_favorite
    db.commit()
    db.refresh(gen)
    return gen

@router.delete("/generations/{gen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation(gen_id: str, db: Session = Depends(get_db)):
    """
    Removes a generation record from the DB.
    """
    gen = db.query(Generation).filter(Generation.id == gen_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    db.delete(gen)
    db.commit()
    return

# --- Custom Presets ---

@router.get("/presets", response_model=List[PresetResponse])
def list_presets(db: Session = Depends(get_db)):
    """
    Returns all configured presets. Includes default configurations.
    """
    presets = db.query(Preset).all()
    # If no presets exist, create some standard ones
    if not presets:
        default_presets = [
            Preset(
                name="Ericksonian Flow",
                description="Indirect, permissive suggestions with a calming ocean breeze.",
                style="Ericksonian",
                voice="deep_male",
                music_theme="ocean",
                binaural_freq="theta",
                session_length=15
            ),
            Preset(
                name="Deep Sleep Induction",
                description="Slow progressive count down with theta/delta layers for sleep.",
                style="Sleep Induction",
                voice="slow_whispers",
                music_theme="rain",
                binaural_freq="delta",
                session_length=20
            ),
            Preset(
                name="Confidence Boost NLP",
                description="Empowering direct suggestion with motivational drone layers.",
                style="Confidence Boost",
                voice="warm_conversational",
                music_theme="meditation_pads",
                binaural_freq="alpha",
                session_length=10
            )
        ]
        for dp in default_presets:
            db.add(dp)
        db.commit()
        presets = db.query(Preset).all()
    return presets

@router.post("/presets", response_model=PresetResponse, status_code=status.HTTP_201_CREATED)
def create_preset(payload: PresetCreate, db: Session = Depends(get_db)):
    db_preset = Preset(
        name=payload.name,
        description=payload.description,
        style=payload.style,
        voice=payload.voice,
        music_theme=payload.music_theme,
        binaural_freq=payload.binaural_freq,
        session_length=payload.session_length
    )
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset

@router.delete("/presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(preset_id: str, db: Session = Depends(get_db)):
    preset = db.query(Preset).filter(Preset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    db.delete(preset)
    db.commit()
    return
