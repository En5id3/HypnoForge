import os
import asyncio
import sys

# Add the project root to sys.path so we can import backend packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.rewriter import rewriter
from backend.app.services.tts_service import tts_service
from backend.app.services.audio_engine import audio_engine
from backend.app.services.video_engine import video_engine
from backend.app.services.transcribe_service import transcribe_service

async def run_test():
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_test")
    os.makedirs(test_dir, exist_ok=True)
    
    print("=== HYPNOFORGE PIPELINE INTEGRATION TEST ===")
    
    # 1. Rewriter test
    print("\n1. Running script rewriter...")
    prompt = "Release all tension and stress from the day"
    script = rewriter._generate_fallback_script(prompt, "Ericksonian", 1)
    # Shorten the script for a fast test run
    short_script = "[speed:0.95] Take a deep breath. [pause:2] Feel the calm ocean waves. [speed:0.85] Relax completely. [pause:3]"
    print(f"Test script: {short_script}")
    
    # 2. TTS Narration test
    print("\n2. Synthesizing voice narration...")
    narration_wav, captions = await tts_service.generate_narration(short_script, "deep_male", test_dir)
    print(f"Narration WAV generated: {narration_wav} (Exists: {os.path.exists(narration_wav)})")
    print(f"Captions generated: {captions}")
    
    # 3. Audio layering test
    print("\n3. Generating ambient tracks and layering audio...")
    final_mp3 = audio_engine.compile_hypnosis_session(narration_wav, "ocean", "theta", test_dir)
    print(f"Final MP3 generated: {final_mp3} (Exists: {os.path.exists(final_mp3)})")
    
    # 4. SRT transcription test
    print("\n4. Generating SRT subtitles...")
    srt_path = os.path.join(test_dir, "test.srt")
    transcribe_service.generate_srt(captions, srt_path)
    print(f"SRT generated: {srt_path} (Exists: {os.path.exists(srt_path)})")
    
    # 5. Video Loop generation (render 24 frames for a fast test, i.e., 1 second loop)
    print("\n5. Rendering looping visual video...")
    # Temporarily set total frames to 24 for fast test
    original_total = video_engine.total_frames
    video_engine.total_frames = 24  # 1 second of video
    try:
        loop_mp4 = os.path.join(test_dir, "loop.mp4")
        video_engine.generate_loop_video(loop_mp4)
        print(f"Loop MP4 generated: {loop_mp4} (Exists: {os.path.exists(loop_mp4)})")
        
        # 6. Final Video Stitching test
        print("\n6. Muxing video and audio...")
        final_mp4 = os.path.join(test_dir, "session_final.mp4")
        video_engine.render_final_video(loop_mp4, final_mp3, final_mp4)
        print(f"Final MP4 video generated: {final_mp4} (Exists: {os.path.exists(final_mp4)})")
        
    finally:
        video_engine.total_frames = original_total
        
    print("\n=== PIPELINE TEST COMPLETED SUCCESSFULLY ===")
    print(f"Outputs generated in: {test_dir}")
    print(f"  - MP3 Size: {os.path.getsize(final_mp3)} bytes")
    print(f"  - MP4 Size: {os.path.getsize(final_mp4)} bytes")
    print(f"  - SRT Size: {os.path.getsize(srt_path)} bytes")

if __name__ == "__main__":
    asyncio.run(run_test())
