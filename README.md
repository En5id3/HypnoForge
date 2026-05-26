# HypnoForge // Cosmic Hypnosis Content Factory

HypnoForge is a full-stack, AI-powered web application designed to serve as a high-fidelity "YouTube hypnosis content factory." Users can enter simple text prompts or custom clinical scripts to generate finished media assets: hypnotic voiceovers, custom brainwave frequencies (Delta/Theta binaural beats), ambient music beds, synchronized subtitle files (.srt), and high-definition looping cosmic visual video packages (.mp4) in seconds.

---

## 1. System Architecture Plan

HypnoForge follows a modular microservice architecture designed for local development and cost-effective scaling:

```
                  ┌──────────────────────────────────────────────┐
                  │                 Vite React                   │
                  │              (Cinematic UI)                  │
                  └──────────────────────┬───────────────────────┘
                                         │ REST API / JSON
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │                FastAPI Host                  │
                  │             (Async Pipeline)                 │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
     ┌──────────────────────┐┌──────────────────────┐┌──────────────────────┐
     │  AI Rewriter         ││  Voice TTS Service   ││  Audio/Video Engine  │
     │  (Gemini API /       ││  (Edge-TTS /         ││  (NumPy Synthesis /  │
     │  Template Engine)    ││   Pacing Filter)     ││   FFmpeg Mixers)     │
     └──────────────────────┘└──────────────────────┘└──────────────────────┘
```

### Modular Components:
*   **Frontend Studio**: A cinematic meditation-themed React workstation. Features script editing, customized tuning panels (frequencies, voices, soundscapes), and media visualizers.
*   **FastAPI Pipeline Orchestrator**: Handles asynchronous generation requests, dispatches background threads, monitors progress status, and updates SQLite.
*   **AI Hypnosis Rewriter**: Conversational engine wrapping raw input topics in clinical permissive patterns, trance loops, and pacing cues.
*   **TTS Pacing Engine**: Splits script tags, fetches TTS voice streams, and executes FFmpeg tempo scaling.
*   **Audio Synthesis Engine**: Generates Delta/Theta binaural beat stereo WAVs programmatically and mixes them with ambient noise.
*   **Video Loop Generator**: Spawns a high-quality 10-second repeating visual loop and uses copy-codec muxing to export 30-minute videos instantly.

---

## 2. Folder Structure

```
HypnoFaux/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── history.py       # Dashboard, favoriting, preset endpoints
│   │   │   │   └── hypnosis.py      # Script rewriter, pipeline, status endpoints
│   │   │   └── router.py            # Primary endpoints compiler
│   │   ├── services/
│   │   │   ├── audio_engine.py      # Binaural generation & multi-track mixing
│   │   │   ├── rewriter.py          # Gemini AI hypnosis script expander
│   │   │   ├── transcribe_service.py # SRT timestamp alignment compiler
│   │   │   ├── tts_service.py       # edge-tts voice worker & tempo scaling
│   │   │   └── video_engine.py      # Pillow frame loop renderer & muxer
│   │   ├── config.py                # Environment configs & directories
│   │   ├── database.py              # SQLite configuration
│   │   ├── main.py                  # API entrance & static mount
│   │   ├── models.py                # Database entity mappings
│   │   └── schemas.py               # Pydantic schemas
│   ├── requirements.txt             # Python backend dependencies
│   └── Dockerfile                   # Python, FFmpeg, Piper environments
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CustomizationPanel.jsx # Voice, music, and brainwave sliders
│   │   │   ├── Dashboard.jsx        # History lists & stats trackers
│   │   │   ├── PlayerPreview.jsx     # Progress widgets, players, and downloaders
│   │   │   ├── ScriptInput.jsx      # Prompt entry & tag-highlighted text editor
│   │   │   └── Sidebar.jsx          # Futuristic navigation bar
│   │   ├── App.jsx                  # Root state layer & workspace grids
│   │   ├── index.css                # Base Tailwind rules & keyframe glows
│   │   └── main.jsx                 # Client entrypoint
│   ├── package.json                 # Frontend dependencies (React, Vite, Tailwind)
│   ├── tailwind.config.js           # Theme custom overrides
│   ├── postcss.config.js            # PostCSS compiler rules
│   ├── vite.config.js               # Dev-server proxy setups
│   └── Dockerfile                   # Node Vite runner
├── docker-compose.yml               # Service compiler
└── README.md                        # Documentation
```

---

## 3. Database Schema

HypnoForge uses **SQLite** for light-footprint local storage.

### Table: `generations`
Tracks each pipeline execution, media paths, and favorites.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key (UUID) |
| `prompt` | TEXT | Raw input session topic |
| `rewritten_script`| TEXT | Expanded clinical hypnosis script |
| `style` | VARCHAR(50) | Erickson, Sleep, Confidence, NLP, etc. |
| `voice` | VARCHAR(50) | Character voice profile key |
| `music_theme` | VARCHAR(50) | Rain, Ocean, Cosmic, Tibetan, etc. |
| `binaural_freq` | VARCHAR(50) | Delta, Theta, Alpha, None |
| `session_length` | INTEGER | Session duration in minutes |
| `status` | VARCHAR(30) | pending, rewriting, synthesizing, video, completed, failed |
| `audio_url` | VARCHAR(255) | Static download path to MP3 |
| `video_url` | VARCHAR(255) | Static download path to MP4 |
| `subtitles_url` | VARCHAR(255) | Static download path to SRT |
| `error_message` | TEXT | Exception call stack for debugs |
| `is_favorite` | BOOLEAN | Star/unstar tag |
| `created_at` | DATETIME | Timestamp of execution |

### Table: `presets`
Provides customizable configuration presets.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key (UUID) |
| `name` | VARCHAR(100) | Preset display name |
| `description` | VARCHAR(255) | Subtext summary |
| `style` | VARCHAR(50) | Hypnosis style presets |
| `voice` | VARCHAR(50) | Character voice profile key |
| `music_theme` | VARCHAR(50) | Ambient music theme |
| `binaural_freq` | VARCHAR(50) | Brainwave category |
| `session_length` | INTEGER | Preset duration in minutes |
| `created_at` | DATETIME | Timestamp |

---

## 4. API Design

### Hypnosis Generation Router
*   `POST /api/rewrite`: Synchronously rewrite script topics.
    *   **Payload**: `{ "prompt": "str", "style": "str", "session_length": int }`
    *   **Response**: `{ "rewritten_script": "str" }`
*   `POST /api/generate`: Starts the background synthesis pipeline.
    *   **Payload**: `{ "prompt": "str", "custom_script": "str", "style": "str", "voice": "str", "music_theme": "str", "binaural_freq": "str", "session_length": int }`
    *   **Response**: Returns the `Generation` object with `status: pending` (201 Created).
*   `GET /api/status/{gen_id}`: Polls the state of the active run.
    *   **Response**: Returns the updated `Generation` DB object.

### Dashboard & Library Router
*   `GET /api/generations`: Lists history logs (newest first).
*   `GET /api/generations/{gen_id}`: Fetch detailed generation log.
*   `PUT /api/generations/{gen_id}/favorite`: Toggle `is_favorite` boolean status.
*   `DELETE /api/generations/{gen_id}`: Deletes SQLite entry and logs.
*   `GET /api/presets`: Retrieve custom preset templates.
*   `POST /api/presets`: Store current settings as a new configuration preset.
*   `DELETE /api/presets/{preset_id}`: Remove preset.

---

## 5. Audio & Video Engine (FFmpeg Workflows)

### A. Pacing/Speed Adjustment (tempo modification)
During narration synthesis, text segments are slowed down to induce deep trance states. We apply FFmpeg's frequency-preserving `atempo` filter:
```bash
ffmpeg -y -i segment_raw.mp3 -filter:a "atempo=0.85,aresample=44100" -ac 2 -acodec pcm_s16le segment_processed.wav
```

### B. Multi-Track Layering & Mixing
Narration, procedural ambient background music, and binaural frequency layers are combined.
*   *Narration* is kept at full gain (1.0).
*   *Music Ambience* is lowered to (0.45) for comfortable reading.
*   *Binaural Beats* are placed at (0.20) as a low hum.
```bash
ffmpeg -y -i narration.wav -i ambient.wav -i binaural.wav \
  -filter_complex "[0:a]volume=1.0[a0];[1:a]volume=0.45[a1];[2:a]volume=0.20[a2];[a0][a1][a2]amix=inputs=3:duration=first:dropout_transition=5[a]" \
  -map "[a]" -b:a 192k session_final.mp3
```

### C. Looping Video Render
Generating 30-minute videos typically demands high resources. We optimize this by rendering a **10-second looping animation** in Python and stream-looping it infinitely while copying the stream headers to avoid re-encoding:
```bash
ffmpeg -y -stream_loop -1 -i loop_visual.mp4 -i session_final.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -shortest session_final.mp4
```
> [!TIP]
> Using `-c:v copy` means the video is not re-encoded. FFmpeg only copies the pre-rendered frames. A 30-minute 1080p cosmic video compilation completes in **under 2 seconds**.

---

## 6. Procedural Audio & Video Generation (NumPy / Pillow)

### Binaural Beat Generator
Binaural beats require stereo audio. NumPy generates sine waves for left and right channels with a frequency delta corresponding to target brainwaves (e.g. 150 Hz left, 156 Hz right for a 6 Hz Theta wave):
$$t \in [0, \text{duration}]$$
$$\text{Left}(t) = \sin(2\pi \cdot f_c \cdot t), \quad \text{Right}(t) = \sin(2\pi \cdot (f_c + \Delta f) \cdot t)$$
The resulting arrays are scaled, converted to 16-bit PCM, and written directly using SciPy.

### Ambient Synth Bed
Ambient audio layers are synthesised programmatically to bypass copyright or asset dependencies:
*   **Rain**: Synthesised using white noise, convolved with a rolling average to act as a soft lowpass filter, and modulated by an 8-second LFO to simulate wind gusts.
*   **Ocean**: Brown noise generated by integrating random distributions, modulated by a slow 10-second swell LFO.
*   **Meditation Pads**: C-Minor 9th chord overlay (frequencies 130.81Hz, 155.56Hz, 196.00Hz, 233.08Hz, 293.66Hz) modulated by multiple phase-shifted sinusoidal LFOs.
*   **Symphonic Widener**: We apply a **4.5ms phase delay** to the right channel (`np.roll` by 200 samples) to create an immersive, wide stereo field.

---

## 7. Sample Prompts & Styles

Here are a few sample prompts to feed into the generator:

*   **Deep Sleep Induction**:
    *   *Prompt*: "Deep sleep hypnosis for curing insomnia, letting go of today's thoughts, and drifting into deep restorative rest."
    *   *Style*: Sleep Induction
*   **Confidence Boost**:
    *   *Prompt*: "Confidence and self-worth hypnosis to reprogram the subconscious, release self-doubt, and stand tall in my true power."
    *   *Style*: Confidence Boost
*   **Anxiety Relief**:
    *   *Prompt*: "Relieving sensory panic, calming the nervous system, and releasing tension from the shoulders and chest."
    *   *Style*: Anxiety Relief
*   **Ericksonian Flow**:
    *   *Prompt*: "Letting go of control, allowing changes to happen automatically, and relaxing without even trying."
    *   *Style*: Ericksonian

---

## 8. Installation & Setup

Ensure you have **Docker** and **docker-compose** installed on your system.

### Running with Docker

1.  **Clone or navigate** to the project directory:
    ```bash
    cd /Users/ashishverma/Assignment1/HypnoFaux
    ```

2.  *(Optional)* Create a `.env` file at the project root and add your Gemini API Key:
    ```bash
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
    *(Note: If no API key is specified, HypnoForge automatically falls back to its procedural clinical template rewriter).*

3.  **Boot the services** using Docker Compose:
    ```bash
    docker-compose up --build
    ```

4.  **Access the applications**:
    *   **Frontend Cinematic Workstation**: [http://localhost:5173](http://localhost:5173)
    *   **Backend API documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

5.  All generated MP3s, MP4s, subtitle SRTs, and the SQL database are persisted locally in your project folder under `./static/` and `./output/`.

---

## 9. MVP Roadmap & Future Scaling Recommendations

### Phase 1: MVP Core (Current)
*   Procedural synthesis of binaural beats and wide ambient themes.
*   Edge-TTS voice generator with custom speed and pause tags.
*   10-second visual loops with copy-codec muxing.
*   SQLite session history and preset template managers.

### Phase 2: Production Scaling
1.  **Distributed Queue Task Processing**:
    *   Migrate background processing tasks from FastAPI `BackgroundTasks` to a distributed queue like **Celery** with **Redis** or **RabbitMQ**.
    *   Allows spinning up multiple worker nodes on GPUs to handle high visual rendering volume.
2.  **Voice Cloning & Advanced Local TTS**:
    *   Integrate a local Docker worker running **Piper TTS** (for fast, offline CPU-based voices) or **Coqui XTTS v2** (for high-fidelity voice cloning).
3.  **Video Rendering Upgrade**:
    *   Integrate **SVD (Stable Video Diffusion)** or WebGL-based Canvas recording to generate fully dynamic visual animations on the fly.
4.  **Automated YouTube API Publisher**:
    *   Add OAuth2 credentials to the dashboard, allowing creators to publish generated MP4 videos directly to YouTube/TikTok as Scheduled Uploads or Shorts.
