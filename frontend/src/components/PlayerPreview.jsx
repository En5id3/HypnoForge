import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Download, Video, Music, Subtitles, HelpCircle, RefreshCw, Film, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

export default function PlayerPreview({ 
  prompt, 
  script, 
  style, 
  voice, 
  musicTheme, 
  binauralFreq, 
  sessionLength,
  onGenerationComplete
}) {
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeMedia, setActiveMedia] = useState('video'); // 'video' or 'audio'
  
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const pollIntervalRef = useRef(null);

  const getStatusMessage = (status) => {
    switch (status) {
      case 'pending': return 'Initializing workspace...';
      case 'rewriting': return 'Analyzing script context and expanding suggestions...';
      case 'synthesizing': return 'Generating narration track (applying emotional pacing)...';
      case 'layering': return 'Synthesizing ambient backing track and binaural beats...';
      case 'video': return 'Rendering abstract cosmic visual loops & muxing files...';
      case 'completed': return 'Session forged successfully!';
      default: return 'Processing...';
    }
  };

  const getProgressPercentage = (status) => {
    switch (status) {
      case 'pending': return 10;
      case 'rewriting': return 25;
      case 'synthesizing': return 50;
      case 'layering': return 75;
      case 'video': return 90;
      case 'completed': return 100;
      default: return 0;
    }
  };

  const triggerGenerate = async () => {
    setLoading(true);
    setError(null);
    setTask(null);
    setIsPlaying(false);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt || `Hypnosis session: ${style}`,
          custom_script: script || null,
          style,
          voice,
          music_theme: musicTheme,
          binaural_freq: binauralFreq,
          session_length: sessionLength
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit generation task. Verify backend is running.');
      }

      const data = await response.json();
      setTask(data);
      
      // Start polling
      startPolling(data.id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const startPolling = (taskId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`/api/status/${taskId}`);
        if (!response.ok) throw new Error('Status check failed');
        
        const data = await response.json();
        setTask(data);
        
        if (data.status === 'completed') {
          clearInterval(pollIntervalRef.current);
          setLoading(false);
          if (onGenerationComplete) onGenerationComplete();
        } else if (data.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          setError(data.error_message || 'Backend generation failed.');
          setLoading(false);
        }
      } catch (err) {
        logger.error("Polling error:", err);
      }
    }, 2000);
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  const togglePlayback = () => {
    if (activeMedia === 'video' && videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    } else if (activeMedia === 'audio' && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="space-y-6">
      {/* Trigger Control */}
      {!task && !loading && (
        <div className="glass-panel p-8 rounded-2xl text-center space-y-5 border border-indigo-500/25 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none"></div>
          
          <div className="mx-auto w-16 h-16 bg-indigo-600/10 rounded-2xl flex items-center justify-center border border-indigo-500/30 shadow-glow mb-2">
            <Film className="w-8 h-8 text-indigo-400" />
          </div>
          
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-lg font-bold text-slate-200">Ready to Forge Media?</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Compile your written suggestions, customized binaural waveforms, ambient textures, and abstract visual render loop into a cohesive YouTube-ready file.
            </p>
          </div>

          <button
            onClick={triggerGenerate}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-slate-100 font-semibold text-sm py-3 px-8 rounded-xl border border-indigo-500/30 shadow-glow transition-all duration-300 transform hover:scale-[1.02]"
          >
            <span>Generate Hypnosis Session</span>
            <ArrowRight className="w-4 h-4 text-indigo-200" />
          </button>
        </div>
      )}

      {/* Loading & Rendering State */}
      {loading && task && (
        <div className="glass-panel p-8 rounded-2xl space-y-6 border border-purple-500/25">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-5 h-5 text-purple-400 animate-spin" />
              <div>
                <h4 className="text-sm font-bold text-slate-200">Forging Content Package</h4>
                <p className="text-[10px] text-slate-400 font-mono mt-0.5">{task.id}</p>
              </div>
            </div>
            <span className="text-xs font-mono text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2.5 py-1 rounded-full uppercase tracking-wider font-semibold">
              {task.status}
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-300">
              <span>{getStatusMessage(task.status)}</span>
              <span>{getProgressPercentage(task.status)}%</span>
            </div>
            {/* Progress bar container */}
            <div className="h-2 bg-dark-600 rounded-full overflow-hidden border border-slate-800">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-teal-500 transition-all duration-500 rounded-full"
                style={{ width: `${getProgressPercentage(task.status)}%` }}
              ></div>
            </div>
          </div>

          {/* Animated placeholder workspace representation */}
          <div className="p-4 bg-dark-800/80 rounded-xl border border-slate-800/60 flex items-center justify-center min-h-[140px] relative overflow-hidden">
            <div className="absolute inset-0 bg-radial-gradient flex items-center justify-center">
              <div className="w-20 h-20 border border-indigo-500/30 rounded-full animate-ping opacity-25"></div>
            </div>
            <div className="text-center space-y-1 relative z-10 animate-pulse-slow">
              <Film className="w-8 h-8 text-indigo-400/60 mx-auto" />
              <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mt-2">Rendering Pipeline Engaged</p>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="glass-panel p-8 rounded-2xl border border-red-500/30 space-y-4">
          <div className="flex items-center gap-3">
            <div className="bg-red-500/10 p-2.5 rounded-xl border border-red-500/20">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-200">Media Generation Failed</h4>
              <p className="text-xs text-slate-400">An error occurred within the rendering pipeline.</p>
            </div>
          </div>
          <div className="p-4 bg-red-950/20 rounded-xl border border-red-500/10 text-xs font-mono text-red-300/80 whitespace-pre-wrap max-h-40 overflow-y-auto leading-relaxed">
            {error}
          </div>
          <button 
            onClick={triggerGenerate}
            className="w-full bg-dark-600 hover:bg-slate-800 text-slate-200 text-xs font-semibold py-2.5 px-4 rounded-xl border border-slate-800 transition-colors"
          >
            Retry Session Generation
          </button>
        </div>
      )}

      {/* Completed State (Player & Downloads) */}
      {task && task.status === 'completed' && (
        <div className="glass-panel p-6 rounded-2xl space-y-6 border border-teal-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-teal-400" />
              <h4 className="text-sm font-bold text-slate-200">Generation Complete</h4>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => setActiveMedia('video')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  activeMedia === 'video' 
                    ? 'bg-teal-500/10 border-teal-500/30 text-teal-300' 
                    : 'bg-dark-600 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Video className="w-3.5 h-3.5" /> Video
              </button>
              <button 
                onClick={() => setActiveMedia('audio')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  activeMedia === 'audio' 
                    ? 'bg-teal-500/10 border-teal-500/30 text-teal-300' 
                    : 'bg-dark-600 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Music className="w-3.5 h-3.5" /> Audio
              </button>
            </div>
          </div>

          {/* Media Player Display */}
          <div className="bg-dark-950 rounded-xl overflow-hidden border border-slate-800/80 relative group aspect-video flex items-center justify-center">
            {activeMedia === 'video' && task.video_url && (
              <video
                ref={videoRef}
                src={task.video_url}
                className="w-full h-full object-cover"
                controls
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              >
                {task.subtitles_url && (
                  <track 
                    label="English Subtitles" 
                    kind="subtitles" 
                    srcLang="en" 
                    src={task.subtitles_url} 
                    default 
                  />
                )}
              </video>
            )}

            {activeMedia === 'audio' && task.audio_url && (
              <div className="w-full h-full flex flex-col items-center justify-center p-8 space-y-6 relative overflow-hidden">
                {/* Floating ambient aura background */}
                <div className="absolute w-48 h-48 rounded-full bg-teal-500/10 filter blur-3xl animate-pulse-slow z-0"></div>
                
                <div className="w-20 h-20 bg-dark-800 rounded-full flex items-center justify-center border border-slate-800 shadow-glow-teal relative z-10 animate-slow-rotate">
                  <Music className="w-8 h-8 text-teal-400" />
                </div>
                
                <audio
                  ref={audioRef}
                  src={task.audio_url}
                  className="w-full max-w-md relative z-10"
                  controls
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />
              </div>
            )}
          </div>

          {/* Exports Download Panel */}
          <div className="space-y-3">
            <h5 className="text-[11px] font-bold text-slate-400 tracking-wider uppercase">Export Session Files</h5>
            <div className="grid grid-cols-3 gap-3">
              {task.audio_url && (
                <a
                  href={task.audio_url}
                  download={`HypnoForge_Session_${task.id}.mp3`}
                  className="flex items-center justify-center gap-2 bg-dark-600 hover:bg-slate-800 text-slate-200 text-xs font-semibold py-3 px-4 rounded-xl border border-slate-800 transition-colors"
                >
                  <Music className="w-4 h-4 text-teal-400" />
                  <span>MP3 Audio</span>
                </a>
              )}
              {task.video_url && (
                <a
                  href={task.video_url}
                  download={`HypnoForge_Session_${task.id}.mp4`}
                  className="flex items-center justify-center gap-2 bg-dark-600 hover:bg-slate-800 text-slate-200 text-xs font-semibold py-3 px-4 rounded-xl border border-slate-800 transition-colors"
                >
                  <Video className="w-4 h-4 text-indigo-400" />
                  <span>MP4 Video</span>
                </a>
              )}
              {task.subtitles_url && (
                <a
                  href={task.subtitles_url}
                  download={`HypnoForge_Subtitles_${task.id}.srt`}
                  className="flex items-center justify-center gap-2 bg-dark-600 hover:bg-slate-800 text-slate-200 text-xs font-semibold py-3 px-4 rounded-xl border border-slate-800 transition-colors"
                >
                  <Subtitles className="w-4 h-4 text-purple-400" />
                  <span>SRT Captions</span>
                </a>
              )}
            </div>
          </div>
          
          <button 
            onClick={() => setTask(null)}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-slate-100 text-xs font-semibold py-2.5 px-4 rounded-xl shadow-glow transition-all"
          >
            Create New Generation
          </button>
        </div>
      )}
    </div>
  );
}
