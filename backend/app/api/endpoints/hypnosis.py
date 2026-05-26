import os
import shutil
import logging
import traceback
from typing import Union
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Generation
from backend.app.schemas import RewriteRequest, RewriteResponse, GenerationCreate, GenerationResponse
from backend.app.services.rewriter import rewriter
from backend.app.services.tts_service import tts_service
from backend.app.services.audio_engine import audio_engine
from backend.app.services.video_engine import video_engine
from backend.app.services.transcribe_service import transcribe_service
from backend.app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Helper function for updating Generation DB records in background
def update_generation_status(gen_id: str, status: str, db: Session, **kwargs):
    gen = db.query(Generation).filter(Generation.id == gen_id).first()
    if gen:
        gen.status = status
        for key, value in kwargs.items():
            setattr(gen, key, value)
        db.commit()

async def run_generation_pipeline(gen_id: str, prompt: str, custom_script: Union[str, None], style: str, voice: str, music_theme: str, binaural_freq: str, session_length: int, audio_speed: float, audio_pitch: float, audio_calmness: int, ambient_volume: float, db: Session):
    # Create local temporary task directory
    task_dir = os.path.join(settings.OUTPUT_DIR, f"task_{gen_id}")
    os.makedirs(task_dir, exist_ok=True)
    
    try:
        # Step 1: Rewriting
        update_generation_status(gen_id, "rewriting", db)
        if custom_script:
            script = custom_script
        else:
            script = rewriter.rewrite(prompt, style, session_length)
            
        update_generation_status(gen_id, "synthesizing", db, rewritten_script=script)
        
        # Step 2: Synthesis of voice narration (with speed, pitch, calmness pacing)
        # Returns path to narration wav and list of timed captions
        narration_wav, captions = await tts_service.generate_narration(script, voice, task_dir, speed_factor=audio_speed, pitch_factor=audio_pitch, calmness_factor=audio_calmness)
        
        # Step 3: Layering ambient music & binaural frequencies
        update_generation_status(gen_id, "layering", db)
        final_mp3_local = audio_engine.compile_hypnosis_session(narration_wav, music_theme, binaural_freq, task_dir, calmness=audio_calmness, ambient_volume=ambient_volume)
        
        # Move final audio to static directory
        static_audio_dir = os.path.join(settings.STATIC_DIR, "audio")
        os.makedirs(static_audio_dir, exist_ok=True)
        audio_filename = f"{gen_id}.mp3"
        dest_audio_path = os.path.join(static_audio_dir, audio_filename)
        shutil.move(final_mp3_local, dest_audio_path)
        audio_url = f"/static/audio/{audio_filename}"
        
        # Step 4: Write Subtitle File (SRT)
        srt_filename = f"{gen_id}.srt"
        static_sub_dir = os.path.join(settings.STATIC_DIR, "subtitles")
        os.makedirs(static_sub_dir, exist_ok=True)
        dest_srt_path = os.path.join(static_sub_dir, srt_filename)
        transcribe_service.generate_srt(captions, dest_srt_path)
        subtitles_url = f"/static/subtitles/{srt_filename}"
        
        # Step 5: Render Video
        update_generation_status(gen_id, "video", db, audio_url=audio_url, subtitles_url=subtitles_url)
        
        loop_mp4_local = os.path.join(task_dir, "loop_temp.mp4")
        video_engine.generate_loop_video(loop_mp4_local)
        
        static_video_dir = os.path.join(settings.STATIC_DIR, "video")
        os.makedirs(static_video_dir, exist_ok=True)
        video_filename = f"{gen_id}.mp4"
        dest_video_path = os.path.join(static_video_dir, video_filename)
        
        # Mux 10s visual loop and final audio using copy codec
        video_engine.render_final_video(loop_mp4_local, dest_audio_path, dest_video_path)
        video_url = f"/static/video/{video_filename}"
        
        # Complete
        update_generation_status(gen_id, "completed", db, video_url=video_url)
        logger.info(f"Pipeline completed successfully for generation: {gen_id}")
        
    except Exception as e:
        error_msg = f"Generation failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        update_generation_status(gen_id, "failed", db, error_message=error_msg)
        
    finally:
        # Clean up local task directory
        if os.path.exists(task_dir):
            shutil.rmtree(task_dir)

@router.post("/rewrite", response_model=RewriteResponse)
def rewrite_script(payload: RewriteRequest):
    """
    Synchronously rewrite raw prompt into hypnotic script.
    """
    try:
        script = rewriter.rewrite(payload.prompt, payload.style, payload.session_length)
        return RewriteResponse(rewritten_script=script)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rewriter failed: {str(e)}"
        )

@router.post("/generate", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
def start_generation(payload: GenerationCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers the asynchronous pipeline to generate audio, video, and subtitles.
    """
    # Create DB entry
    db_gen = Generation(
        prompt=payload.prompt,
        rewritten_script=payload.custom_script,
        style=payload.style,
        voice=payload.voice,
        music_theme=payload.music_theme,
        binaural_freq=payload.binaural_freq,
        session_length=payload.session_length,
        audio_speed=payload.audio_speed,
        audio_pitch=payload.audio_pitch,
        audio_calmness=payload.audio_calmness,
        ambient_volume=payload.ambient_volume,
        status="pending"
    )
    db.add(db_gen)
    db.commit()
    db.refresh(db_gen)
    
    # Run async pipeline task
    background_tasks.add_task(
        run_generation_pipeline,
        db_gen.id,
        db_gen.prompt,
        payload.custom_script,
        db_gen.style,
        db_gen.voice,
        db_gen.music_theme,
        db_gen.binaural_freq,
        db_gen.session_length,
        db_gen.audio_speed,
        db_gen.audio_pitch,
        db_gen.audio_calmness,
        db_gen.ambient_volume,
        db
    )
    
    return db_gen

@router.get("/status/{gen_id}", response_model=GenerationResponse)
def get_generation_status(gen_id: str, db: Session = Depends(get_db)):
    """
    Retrieve generation status by ID.
    """
    gen = db.query(Generation).filter(Generation.id == gen_id).first()
    if not gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation ID {gen_id} not found."
        )
    return gen
