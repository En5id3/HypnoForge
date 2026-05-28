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
    "beta": 18.0,  # 18.0 Hz difference (Focus/Awakening)
    "gamma": 40.0, # 40.0 Hz difference (Peak Cognition)
    "epsilon": 0.5, # 0.5 Hz difference (Deep Mystical Union)
    "schumann": 7.83, # 7.83 Hz difference (Schumann Resonance)
    "solfeggio_528": 6.0, # 528 Hz Healing (Theta Difference)
    "cosmic_432": 4.0 # 432 Hz Cosmic (Delta Difference)
}

class AudioEngine:
    def __init__(self):
        self.sample_rate = 44100

    def generate_binaural_beats(self, duration_sec: float, beat_key: str, carrier_freq: float = 110.0) -> np.ndarray:
        """
        Generates a stereo binaural beats track with elegant, organic, breathing properties.
        Adds warm harmonics and low-frequency amplitude modulation to make it feel rich and natural.
        """
        beat_key = beat_key.lower()
        
        # Dynamic, elegant carrier & beat frequency mapping
        if beat_key == "solfeggio_528":
            carrier_freq = 528.0
            beat_freq = 6.0  # Theta healing
        elif beat_key == "cosmic_432":
            carrier_freq = 432.0
            beat_freq = 4.0  # Delta alignment
        elif beat_key == "schumann":
            carrier_freq = 136.1  # Earth Ohm planetary resonance frequency
            beat_freq = 7.83  # Schumann resonance
        elif beat_key == "epsilon":
            carrier_freq = 90.0   # Deep sub-bass grounding
            beat_freq = 0.5   # Epsilon wave
        elif beat_key == "gamma":
            carrier_freq = 180.0
            beat_freq = 40.0  # Gamma wave
        else:
            # Standard mappings
            beat_freq = BINAURAL_MAP.get(beat_key, 0.0)
            # Default warm carriers
            if beat_key == "delta":
                carrier_freq = 100.0  # Deep and warm
            elif beat_key == "theta":
                carrier_freq = 110.0
            elif beat_key == "alpha":
                carrier_freq = 120.0
            elif beat_key == "beta":
                carrier_freq = 140.0
                
        num_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)
        
        if beat_freq == 0.0 or beat_key == "none":
            return np.zeros((num_samples, 2), dtype=np.int16)
        
        # Soft volume to not overpower narration
        volume = 0.07
        
        # Make the tone elegant by adding a warm second harmonic (octave) and a smooth respiration LFO
        # Slow breathing cycle (5.5 seconds respiration: 0.18 Hz LFO)
        breathing_lfo = 0.8 + 0.2 * np.sin(2 * np.pi * 0.18 * t)
        
        # Left channel = base carrier + 20% octave harmonic
        left_wave = np.sin(2 * np.pi * carrier_freq * t) + 0.20 * np.sin(2 * np.pi * (2 * carrier_freq) * t)
        # Right channel = target beat carrier + 20% octave harmonic
        right_wave = np.sin(2 * np.pi * (carrier_freq + beat_freq) * t) + 0.20 * np.sin(2 * np.pi * (2 * (carrier_freq + beat_freq)) * t)
        
        # Normalize and apply LFO breathing volume envelope
        left = (left_wave / 1.20) * volume * breathing_lfo
        right = (right_wave / 1.20) * volume * breathing_lfo
        
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

        elif theme == "crystal_resonance":
            # Quartz crystal singing bowls C major triad: 261.63Hz (C4), 329.63Hz (E4), 392.00Hz (G4), 523.25Hz (C5)
            # Pulsing slowly with independent slow LFOs
            bowl_c = 0.06 * np.sin(2 * np.pi * 261.63 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t))
            bowl_e = 0.04 * np.sin(2 * np.pi * 329.63 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t))
            bowl_g = 0.04 * np.sin(2 * np.pi * 392.00 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.02 * t))
            bowl_c5 = 0.02 * np.sin(2 * np.pi * 523.25 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.015 * t))
            # Shifting crystalline high hum
            crystal_hum = 0.01 * np.sin(2 * np.pi * 1046.50 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))
            mono = bowl_c + bowl_e + bowl_g + bowl_c5 + crystal_hum

        elif theme == "celestial_chimes":
            # Procedural metal wind chimes triggered at random intervals
            chimes = np.zeros(num_samples)
            # Seed strikes deterministically based on duration
            random.seed(int(duration_sec))
            
            strike_indices = []
            curr_idx = int(self.sample_rate * 2)
            while curr_idx < num_samples - int(self.sample_rate * 3.5):
                strike_indices.append(curr_idx)
                # Strike every ~4.5 to 9.0 seconds
                curr_idx += int(self.sample_rate * random.uniform(4.5, 9.0))
                
            for idx in strike_indices:
                freq = random.choice([523.25, 587.33, 659.25, 783.99, 880.00, 1046.50])
                chime_len = int(self.sample_rate * 3.5)
                t_chime = np.linspace(0, 3.5, chime_len, endpoint=False)
                # Exponential decay envelope
                envelope = np.exp(-2.0 * t_chime) * 0.035
                # Add chime harmonic overtone at 2.05x frequency
                wave = np.sin(2 * np.pi * freq * t_chime) + 0.35 * np.sin(2 * np.pi * 2.05 * freq * t_chime)
                end_idx = min(idx + chime_len, num_samples)
                chimes[idx:end_idx] += wave[:end_idx - idx] * envelope[:end_idx - idx]
                
            # Soft atmospheric backing drone
            backing_drone = 0.03 * np.sin(2 * np.pi * 110 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.03 * t))
            mono = chimes + backing_drone

        elif theme == "temple_garden":
            # Deep stream bubbling water + soft wood-flute slides
            noise = np.random.normal(0, 0.08, num_samples)
            # Water lowpass filter
            water = np.convolve(noise, np.ones(15)/15, mode='same')
            water = water * (0.65 + 0.35 * np.sin(2 * np.pi * 0.08 * t))
            
            # Flute-like warm pentatonic shifts
            flute = np.zeros(num_samples)
            segment_len = int(self.sample_rate * 6.0)
            num_segments = int(duration_sec / 6.0) + 1
            random.seed(int(duration_sec))
            for s_idx in range(num_segments):
                # Choose notes from a peaceful Japanese pentatonic scale (A, B, C, E, F)
                note_freq = random.choice([220.0, 246.94, 261.63, 329.63, 349.23, 440.0])
                start_f = int(s_idx * segment_len)
                end_f = min(start_f + segment_len, num_samples)
                if end_f > start_f:
                    curr_len = end_f - start_f
                    t_seg = np.linspace(0, curr_len/self.sample_rate, curr_len, endpoint=False)
                    # Breathing shape envelope for the flute note
                    envelope = 0.02 * np.sin(np.pi * t_seg / (curr_len/self.sample_rate))
                    flute[start_f:end_f] += np.sin(2 * np.pi * note_freq * t_seg) * envelope
                    
            mono = water + flute

        elif theme == "shamanic_heartbeat":
            # Procedural double heartbeat pulse drum at 55 BPM (1.1s cycle)
            heartbeat = np.zeros(num_samples)
            pulse_len = int(self.sample_rate * 1.1)
            num_pulses = int(duration_sec / 1.1) + 1
            
            t_pulse = np.linspace(0, 1.1, pulse_len, endpoint=False)
            p1 = np.exp(-((t_pulse - 0.15) / 0.04) ** 2)
            p2 = 0.65 * np.exp(-((t_pulse - 0.44) / 0.04) ** 2)
            # Low 55Hz drum heartbeat hum
            template = (p1 + p2) * np.sin(2 * np.pi * 55 * t_pulse) * 0.09
            
            for i in range(num_pulses):
                start = int(i * pulse_len)
                end = min(start + pulse_len, num_samples)
                if end > start:
                    heartbeat[start:end] += template[:end - start]
                    
            # Soft warm desert breeze (modulated brown noise) backing
            noise = np.random.normal(0, 0.12, num_samples)
            brown = np.cumsum(noise)
            brown = brown - np.mean(brown)
            brown = brown / np.max(np.abs(brown)) * 0.04
            breeze = brown * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
            
            mono = heartbeat + breeze
            
        else: # Default quiet drone
            mono = 0.04 * np.sin(2 * np.pi * 110 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.02 * t))
            
        # 2. Add Phase Stereo Widening (delay the right channel slightly)
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

    def compile_hypnosis_session(self, narration_path: str, music_theme: str, binaural_freq: str, task_dir: str, calmness: int = 0, ambient_volume: float = 0.45, session_length: int = 0) -> str:
        """
        Synthesizes binaural beats and ambient backing track matching the target session duration.
        Saves intermediate tracks and uses FFmpeg to mix them all down into a final high-quality MP3.
        Adjusts ambient music volume and binaural beats volume based on closeness to "deep calmness" and user selection.
        """
        # 1. Determine narration length
        sr, narration_data = wavfile.read(narration_path)
        duration_sec = len(narration_data) / sr
        
        # The session duration should match the spoken narration exactly (plus a 2.0-second fade-out buffer),
        # so that the audio and video stop within 3 seconds of the script narration ending.
        target_duration = duration_sec + 2.0
            
        logger.info(f"Narration duration: {duration_sec:.2f}s, Target duration: {target_duration:.2f}s. Synthesizing layers...")
        
        # 2. Generate Binaural Beats
        binaural_data = self.generate_binaural_beats(target_duration, binaural_freq)
        binaural_data = self.apply_fades(binaural_data, fade_in_sec=5.0, fade_out_sec=2.5)
        binaural_wav_path = os.path.join(task_dir, "binaural_layer.wav")
        wavfile.write(binaural_wav_path, self.sample_rate, binaural_data)
        
        # 3. Generate Ambient Music Theme
        ambient_data = self.generate_ambient_track(target_duration, music_theme)
        ambient_data = self.apply_fades(ambient_data, fade_in_sec=8.0, fade_out_sec=3.0)
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
            "-filter_complex", f"[0:a]volume=1.0[a0];[1:a]volume={ambient_vol:.2f}[a1];[2:a]volume={binaural_vol:.2f}[a2];[a0][a1][a2]amix=inputs=3:duration=longest:dropout_transition=5[a]",
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
