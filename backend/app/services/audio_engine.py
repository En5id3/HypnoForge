import os
import logging
import subprocess
import numpy as np
from scipy.io import wavfile
from backend.app.config import settings

logger = logging.getLogger(__name__)

BINAURAL_MAP = {
    "none": 0.0,
    "delta": 2.5,  # 2.5 Hz difference (Deep Sleep)
    "theta": 6.0,  # 6.0 Hz difference (Deep Trance)
    "alpha": 10.0, # 10.0 Hz difference (Relaxed State)
    "beta": 18.0   # 18.0 Hz difference (Focus/Awakening)
}

class AudioEngine:
    def __init__(self):
        self.sample_rate = 44100

    def generate_binaural_beats(self, duration_sec: float, beat_key: str, carrier_freq: float = 150.0) -> np.ndarray:
        """
        Generates a stereo binaural beats track.
        Left channel = carrier_freq, Right channel = carrier_freq + beat_freq.
        """
        beat_freq = BINAURAL_MAP.get(beat_key.lower(), 0.0)
        num_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)
        
        if beat_freq == 0.0:
            return np.zeros((num_samples, 2), dtype=np.int16)
        
        # Soft volume to not overpower narration (e.g. 0.08)
        volume = 0.08
        left = np.sin(2 * np.pi * carrier_freq * t) * volume
        right = np.sin(2 * np.pi * (carrier_freq + beat_freq) * t) * volume
        
        # Combine to stereo
        stereo = np.vstack((left, right)).T
        return (stereo * 32767).astype(np.int16)

    def generate_ambient_track(self, duration_sec: float, theme: str) -> np.ndarray:
        """
        Synthesizes procedural ambient sounds using mathematical waveforms and noise generation.
        Avoids external asset requirements.
        """
        num_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)
        theme = theme.lower().replace(" ", "_")
        
        # 1. Base Synthesis
        if theme == "rain":
            # Filtered white noise with low frequency amplitude modulation
            noise = np.random.normal(0, 0.15, num_samples)
            # Soft lowpass using rolling mean (window = 5)
            mono = np.convolve(noise, np.ones(5)/5, mode='same')
            # LFO amplitude modulation to simulate gusts
            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.08 * t)
            mono = mono * lfo
            
        elif theme == "ocean":
            # Deeper brown-ish noise with slow 10-second wave swell cycles
            noise = np.random.normal(0, 0.25, num_samples)
            # Integrate noise to make brown noise
            brown = np.cumsum(noise)
            brown = brown - np.mean(brown)
            brown = brown / np.max(np.abs(brown)) * 0.15
            # Slow LFO (8-second cycle) for tides
            lfo = 0.4 + 0.6 * (0.5 * (1.0 + np.sin(2 * np.pi * 0.125 * t)))
            mono = brown * lfo
            
        elif theme == "cosmic_drones":
            # Low frequency base drone + harmonically related frequencies modulated by slow independent LFOs
            drone1 = 0.08 * np.sin(2 * np.pi * 60 * t)
            drone2 = 0.05 * np.sin(2 * np.pi * 90 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t))
            drone3 = 0.03 * np.sin(2 * np.pi * 150 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.02 * t))
            mono = drone1 + drone2 + drone3
            
        elif theme == "tibetan_ambience":
            # Ethereal singing bowls: 144Hz (base), 216Hz, 288Hz, 432Hz
            bowl1 = 0.07 * np.sin(2 * np.pi * 144 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
            bowl2 = 0.04 * np.sin(2 * np.pi * 216 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t))
            bowl3 = 0.03 * np.sin(2 * np.pi * 288 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.025 * t))
            bowl4 = 0.02 * np.sin(2 * np.pi * 432 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.01 * t))
            mono = bowl1 + bowl2 + bowl3 + bowl4
            
        elif theme in ["meditation_pads", "temple_atmosphere"]:
            # C Minor 9th chord synth pads with shifting sweep filters
            # C3=130.81Hz, Eb3=155.56Hz, G3=196.00Hz, Bb3=233.08Hz, D4=293.66Hz
            c3 = 0.06 * np.sin(2 * np.pi * 130.81 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t))
            eb3 = 0.05 * np.sin(2 * np.pi * 155.56 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.03 * t))
            g3 = 0.04 * np.sin(2 * np.pi * 196.00 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
            bb3 = 0.03 * np.sin(2 * np.pi * 233.08 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.025 * t))
            d4 = 0.02 * np.sin(2 * np.pi * 293.66 * t) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.015 * t))
            mono = c3 + eb3 + g3 + bb3 + d4
            
        elif theme == "forest_ambience":
            # Soft wind (white noise filtered) + tiny chirps modeled by pitch modulated sines
            wind = np.random.normal(0, 0.05, num_samples)
            mono_wind = np.convolve(wind, np.ones(8)/8, mode='same') * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))
            
            # Periodic crickets / birds (sweeps)
            chirp = 0.005 * np.sin(2 * np.pi * (1500 + 400 * np.sin(2 * np.pi * 20 * t)) * t)
            # Gate chirp randomly or with an LFO
            gate = 0.5 * (1.0 + np.sin(2 * np.pi * 0.1 * t))
            gate = np.where(gate > 0.85, 1.0, 0.0)
            
            mono = mono_wind + (chirp * gate)
            
        else: # Default quiet drone
            mono = 0.04 * np.sin(2 * np.pi * 110 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.02 * t))
            
        # 2. Add Phase Stereo Widening (delay the right channel slightly)
        # Shift right channel by ~200 samples (4.5ms) to create immersive wide space
        shift_samples = 200
        left_channel = mono
        right_channel = np.roll(mono, shift_samples)
        
        # Scale to max amplitude ~0.15 to avoid clipping in subsequent mix
        stereo = np.vstack((left_channel, right_channel)).T
        max_val = np.max(np.abs(stereo))
        if max_val > 0:
            stereo = (stereo / max_val) * 0.15
            
        return (stereo * 32767).astype(np.int16)

    def apply_fades(self, audio_data: np.ndarray, fade_in_sec: float = 6.0, fade_out_sec: float = 12.0) -> np.ndarray:
        """
        Applies a clean linear fade-in and fade-out to the audio data.
        """
        length = len(audio_data)
        fade_in_samples = int(fade_in_sec * self.sample_rate)
        fade_out_samples = int(fade_out_sec * self.sample_rate)
        
        # Prevent fades extending past half of track length
        if fade_in_samples + fade_out_samples > length:
            fade_in_samples = length // 4
            fade_out_samples = length // 4
            
        # Linear fade curves
        fade_in_curve = np.linspace(0.0, 1.0, fade_in_samples).reshape(-1, 1)
        fade_out_curve = np.linspace(1.0, 0.0, fade_out_samples).reshape(-1, 1)
        
        # Apply to both channels
        audio_data[:fade_in_samples] = (audio_data[:fade_in_samples] * fade_in_curve).astype(np.int16)
        audio_data[-fade_out_samples:] = (audio_data[-fade_out_samples:] * fade_out_curve).astype(np.int16)
        
        return audio_data

    def compile_hypnosis_session(self, narration_path: str, music_theme: str, binaural_freq: str, task_dir: str, calmness: int = 0, ambient_volume: float = 0.45) -> str:
        """
        Synthesizes binaural beats and ambient backing track matching the narration duration.
        Saves intermediate tracks and uses FFmpeg to mix them all down into a final high-quality MP3.
        Adjusts ambient music volume and binaural beats volume based on closeness to "deep calmness" and user selection.
        """
        # 1. Determine narration length
        sr, narration_data = wavfile.read(narration_path)
        duration_sec = len(narration_data) / sr
        
        logger.info(f"Narration duration: {duration_sec:.2f} seconds. Synthesizing layers...")
        
        # 2. Generate Binaural Beats
        binaural_data = self.generate_binaural_beats(duration_sec, binaural_freq)
        binaural_data = self.apply_fades(binaural_data, fade_in_sec=5.0, fade_out_sec=10.0)
        binaural_wav_path = os.path.join(task_dir, "binaural_layer.wav")
        wavfile.write(binaural_wav_path, self.sample_rate, binaural_data)
        
        # 3. Generate Ambient Music Theme
        ambient_data = self.generate_ambient_track(duration_sec, music_theme)
        ambient_data = self.apply_fades(ambient_data, fade_in_sec=8.0, fade_out_sec=15.0)
        ambient_wav_path = os.path.join(task_dir, "ambient_layer.wav")
        wavfile.write(ambient_wav_path, self.sample_rate, ambient_data)
        
        # 4. Layer & Mix using FFmpeg
        # Adjust volumes based on user-defined ambient_volume and calmness parameter (0 to 10)
        # Normal mix: Narration = 1.0, Ambient = user-selected (e.g. 0.45), Binaural = 0.20
        # Highly calm mix: Ambient gets quieter (attenuated by up to 50%), Binaural hum gets warmer (up to 0.30)
        ambient_vol = ambient_volume * (1.0 - 0.5 * (calmness / 10.0))
        binaural_vol = 0.20 + (calmness / 10.0) * 0.10
        
        final_mp3_path = os.path.join(task_dir, "session_final.mp3")
        cmd = [
            "ffmpeg", "-y",
            "-i", narration_path,
            "-i", ambient_wav_path,
            "-i", binaural_wav_path,
            "-filter_complex", f"[0:a]volume=1.0[a0];[1:a]volume={ambient_vol:.2f}[a1];[2:a]volume={binaural_vol:.2f}[a2];[a0][a1][a2]amix=inputs=3:duration=first:dropout_transition=5[a]",
            "-map", "[a]",
            "-b:a", "192k",
            final_mp3_path
        ]
        
        logger.info(f"Mixing final track with FFmpeg: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"FFmpeg mixing failed: {result.stderr.decode('utf-8')}")
            raise Exception("FFmpeg failed to mix audio layers.")
            
        # Clean up temporary WAVs
        for path in [binaural_wav_path, ambient_wav_path]:
            if os.path.exists(path):
                os.remove(path)
                
        return final_mp3_path

audio_engine = AudioEngine()
