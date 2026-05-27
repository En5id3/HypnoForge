import os
import re
import asyncio
import logging
import subprocess
import numpy as np
from scipy.io import wavfile
import edge_tts
from backend.app.config import settings

logger = logging.getLogger(__name__)

VOICE_MAP = {
    "deep_male": "en-US-GuyNeural",
    "gentle_female": "en-US-JennyNeural",
    "warm_male": "en-US-AndrewNeural",
    "caring_female": "en-US-AvaNeural",
    "relaxed_female": "en-GB-SoniaNeural",
    "british_male": "en-GB-ThomasNeural",
    "australian_female": "en-AU-NatashaNeural",
    "indian_female": "en-IN-NeerjaNeural",
    "hindi_male": "hi-IN-MadhurNeural",
    "hindi_female": "hi-IN-SwaraNeural"
}

class TTSService:
    def __init__(self):
        self.sample_rate = 44100  # Standard audio sample rate

    def parse_script(self, script: str) -> list:
        """
        Parses script and extracts speed modifications, pauses, and text.
        Returns a list of dicts:
        [
          {"type": "speed", "value": 0.85},
          {"type": "text", "value": "Hello world"},
          {"type": "pause", "value": 3.0}
        ]
        """
        # Split by tags
        pattern = r"(\[speed:[\d.]+\]|\[pause:\d+\])"
        tokens = re.split(pattern, script)
        
        parsed = []
        current_speed = 0.90  # Default speed for hypnosis is slightly slower
        
        for token in tokens:
            if not token:
                continue
            
            speed_match = re.match(r"\[speed:([\d.]+)\]", token)
            pause_match = re.match(r"\[pause:(\d+)\]", token)
            
            if speed_match:
                current_speed = float(speed_match.group(1))
                parsed.append({"type": "speed", "value": current_speed})
            elif pause_match:
                parsed.append({"type": "pause", "value": float(pause_match.group(1))})
            else:
                text_clean = token.strip()
                if text_clean:
                    parsed.append({"type": "text", "value": text_clean, "speed": current_speed})
                    
        return parsed

    async def synthesize_text(self, text: str, voice_key: str, output_path: str):
        """
        Calls edge-tts to generate speech MP3.
        """
        voice = VOICE_MAP.get(voice_key, "en-US-GuyNeural")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    def apply_filters_and_format(self, input_path: str, output_path: str, speed: float, pitch: float, calmness: int):
        """
        Uses FFmpeg to apply speed (atempo), pitch (asetrate + relative atempo),
        calmness (lowpass), and resample to 44.1kHz 16-bit stereo WAV.
        """
        speed = max(0.5, min(2.0, speed))
        pitch = max(0.5, min(2.0, pitch))
        
        filters = []
        
        # 1. Pitch & Speed adjustments
        if pitch != 1.0:
            # Normalize the input sample rate to 44100Hz FIRST. This prevents a "chipmunk" tempo acceleration
            # bug when the input stream (e.g. 24000Hz from edge-tts) differs from 44100Hz.
            filters.append("aresample=44100")
            
            # asetrate shifts pitch and changes speed by pitch factor.
            # To achieve final target speed, relative tempo multiplier is speed / pitch.
            target_rate = int(44100 * pitch)
            filters.append(f"asetrate={target_rate}")
            
            tempo_adjust = speed / pitch
            # FFmpeg atempo requires values in [0.5, 2.0]. Chain filters if needed.
            if tempo_adjust < 0.5:
                filters.append("atempo=0.5")
                filters.append(f"atempo={tempo_adjust / 0.5}")
            elif tempo_adjust > 2.0:
                filters.append("atempo=2.0")
                filters.append(f"atempo={tempo_adjust / 2.0}")
            else:
                filters.append(f"atempo={tempo_adjust}")
        else:
            # Simple speed adjustment
            filters.append(f"atempo={speed}")
            
        # 2. Calmness lowpass filter (cuts high harsh frequencies for softer tone)
        if calmness > 0:
            # Map calmness level 1-10 to lowpass cutoff frequency 8000Hz down to 1500Hz
            cutoff = 8000 - (calmness - 1) * (8000 - 1500) / 9
            filters.append(f"lowpass=f={int(cutoff)}")
            
        # 3. Resample to standard 44.1kHz
        filters.append("aresample=44100")
        
        filter_str = ",".join(filters)
        
        # Build FFmpeg command to convert to stereo, 44100Hz, 16-bit PCM WAV
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-filter:a", filter_str,
            "-ac", "2",
            "-acodec", "pcm_s16le",
            output_path
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    async def generate_narration(self, script: str, voice: str, task_dir: str, speed_factor: float = 1.0, pitch_factor: float = 1.0, calmness_factor: int = 0) -> tuple[str, list[dict]]:
        """
        Processes entire script, generating speed-pacing and pause-layering.
        Saves the final narration to task_dir/narration_final.wav.
        Returns a tuple of (final_wav_path, list_of_captions).
        """
        parsed_items = self.parse_script(script)
        
        audio_segments = []
        temp_files = []
        captions = []
        accumulated_time = 0.0
        
        try:
            for idx, item in enumerate(parsed_items):
                if item["type"] == "text":
                    text = item["value"]
                    # Apply global speed multiplier on top of section-based pacing speed
                    speed = item["speed"] * speed_factor
                    
                    # File paths
                    raw_mp3 = os.path.join(task_dir, f"segment_{idx}_raw.mp3")
                    processed_wav = os.path.join(task_dir, f"segment_{idx}_proc.wav")
                    
                    temp_files.extend([raw_mp3, processed_wav])
                    
                    # Synthesize text to MP3
                    await self.synthesize_text(text, voice, raw_mp3)
                    
                    # Apply speed, pitch, and calmness filters using FFmpeg
                    self.apply_filters_and_format(raw_mp3, processed_wav, speed, pitch_factor, calmness_factor)
                    
                    # Read the PCM WAV file
                    sr, data = wavfile.read(processed_wav)
                    audio_segments.append(data)
                    
                    # Record duration and calculate caption boundaries
                    duration = len(data) / self.sample_rate
                    
                    # Split text into 6-word segments for pleasant subtitle display
                    words = text.split()
                    words_per_caption = 6
                    if words:
                        chunks = [words[i:i + words_per_caption] for i in range(0, len(words), words_per_caption)]
                        time_per_word = duration / len(words)
                        chunk_accumulated = accumulated_time
                        for chunk in chunks:
                            chunk_text = " ".join(chunk)
                            chunk_duration = time_per_word * len(chunk)
                            captions.append({
                                "start": chunk_accumulated,
                                "end": chunk_accumulated + chunk_duration,
                                "text": chunk_text
                            })
                            chunk_accumulated += chunk_duration
                            
                    accumulated_time += duration
                    
                elif item["type"] == "pause":
                    duration = item["value"]
                    # Generate stereo silence (channels = 2)
                    silence_samples = int(self.sample_rate * duration)
                    silence_data = np.zeros((silence_samples, 2), dtype=np.int16)
                    audio_segments.append(silence_data)
                    accumulated_time += duration
            
            # Combine all audio arrays
            if audio_segments:
                final_data = np.concatenate(audio_segments, axis=0)
            else:
                # Default empty narration if nothing was processed
                final_data = np.zeros((44100, 2), dtype=np.int16)
                
            final_path = os.path.join(task_dir, "narration_final.wav")
            wavfile.write(final_path, self.sample_rate, final_data)
            return final_path, captions
            
        finally:
            # Clean up intermediate segment files
            for tf in temp_files:
                if os.path.exists(tf):
                    try:
                        os.remove(tf)
                    except Exception as e:
                        logger.error(f"Failed to delete temp file {tf}: {e}")

tts_service = TTSService()
