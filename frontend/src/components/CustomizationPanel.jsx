import React from 'react';
import { Sliders, Volume2, Music, Timer, Zap, VolumeX, CloudRain, Waves, Bell, Space, Eye, Wind, Heart } from 'lucide-react';

export default function CustomizationPanel({
  style, setStyle,
  voice, setVoice,
  musicTheme, setMusicTheme,
  binauralFreq, setBinauralFreq,
  sessionLength, setSessionLength
}) {
  const stylesList = [
    { id: 'Ericksonian', label: 'Ericksonian', desc: 'Permissive suggestions' },
    { id: 'Sleep Induction', label: 'Sleep Induction', desc: 'Guided sleep transitions' },
    { id: 'Confidence Boost', label: 'Confidence Boost', desc: 'Direct empowering NLP' },
    { id: 'Anxiety Relief', label: 'Anxiety Relief', desc: 'Calming sensory grounding' },
    { id: 'Guided Visualization', label: 'Visualization', desc: 'Immersive guided journeys' },
    { id: 'Direct Suggestion', label: 'Direct Suggestion', desc: 'Firm, behavioral commands' }
  ];

  const voicesList = [
    { id: 'deep_male', label: 'Guy Neural', desc: 'Deep, grounding male tone' },
    { id: 'gentle_female', label: 'Jenny Neural', desc: 'Gentle, comforting female voice' },
    { id: 'warm_conversational', label: 'William Neural', desc: 'Warm, conversational style' },
    { id: 'slow_whispers', label: 'Sonia Neural', desc: 'Soft British whisper' }
  ];

  const musicThemes = [
    { id: 'rain', label: 'Rain Ambience', icon: CloudRain, color: 'text-blue-400' },
    { id: 'ocean', label: 'Ocean Waves', icon: Waves, color: 'text-cyan-400' },
    { id: 'cosmic_drones', label: 'Cosmic Drones', icon: Space, color: 'text-indigo-400' },
    { id: 'tibetan_ambience', label: 'Tibetan Bells', icon: Bell, color: 'text-amber-400' },
    { id: 'meditation_pads', label: 'Meditation Pads', icon: Eye, color: 'text-purple-400' },
    { id: 'forest_ambience', label: 'Forest Wind', icon: Wind, color: 'text-emerald-400' },
    { id: 'temple_atmosphere', label: 'Sacred Temple', icon: Heart, color: 'text-rose-400' }
  ];

  const binauralList = [
    { id: 'none', label: 'None', freq: '0 Hz', desc: 'Pure Narration & Ambience' },
    { id: 'delta', label: 'Delta Wave', freq: '2.5 Hz', desc: 'Dreamless Sleep & Recovery' },
    { id: 'theta', label: 'Theta Wave', freq: '6.0 Hz', desc: 'Deep Trance & Visualization' },
    { id: 'alpha', label: 'Alpha Wave', freq: '10.0 Hz', desc: 'Light Relaxation & Focus' }
  ];

  return (
    <div className="space-y-6">
      {/* Customization Header */}
      <div className="glass-panel p-6 rounded-2xl space-y-6">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
            3. Guided Customization Panel
          </h2>
        </div>

        {/* Hypnosis Style */}
        <div className="space-y-3">
          <label className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Hypnosis Script Style</label>
          <div className="grid grid-cols-2 gap-3">
            {stylesList.map((s) => (
              <button
                key={s.id}
                onClick={() => setStyle(s.id)}
                className={`text-left p-3.5 rounded-xl border transition-all duration-300 relative overflow-hidden group ${
                  style === s.id
                    ? 'bg-indigo-600/10 border-indigo-500 shadow-glow'
                    : 'bg-dark-800/40 border-slate-800/60 hover:bg-slate-800/30'
                }`}
              >
                <div className={`font-semibold text-sm transition-colors ${style === s.id ? 'text-indigo-300' : 'text-slate-300'}`}>
                  {s.label}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">{s.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-800/50 my-6"></div>

        {/* Voice Select */}
        <div className="space-y-3">
          <label className="text-xs font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
            <Volume2 className="w-3.5 h-3.5 text-slate-400" /> Voice Type
          </label>
          <div className="grid grid-cols-2 gap-3">
            {voicesList.map((v) => (
              <button
                key={v.id}
                onClick={() => setVoice(v.id)}
                className={`text-left p-3.5 rounded-xl border transition-all duration-300 ${
                  voice === v.id
                    ? 'bg-purple-600/10 border-purple-500 shadow-glow-purple'
                    : 'bg-dark-800/40 border-slate-800/60 hover:bg-slate-800/30'
                }`}
              >
                <div className={`font-semibold text-sm transition-colors ${voice === v.id ? 'text-purple-300' : 'text-slate-300'}`}>
                  {v.label}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">{v.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-800/50 my-6"></div>

        {/* Music Select */}
        <div className="space-y-3">
          <label className="text-xs font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
            <Music className="w-3.5 h-3.5 text-slate-400" /> Ambient Music Theme
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {musicThemes.map((m) => {
              const Icon = m.icon;
              return (
                <button
                  key={m.id}
                  onClick={() => setMusicTheme(m.id)}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border transition-all duration-300 text-center ${
                    musicTheme === m.id
                      ? 'bg-teal-600/10 border-teal-500 shadow-glow-teal'
                      : 'bg-dark-800/40 border-slate-800/60 hover:bg-slate-800/30'
                  }`}
                >
                  <Icon className={`w-5 h-5 mb-2 ${musicTheme === m.id ? m.color : 'text-slate-500'}`} />
                  <span className={`text-[11px] font-medium transition-colors ${musicTheme === m.id ? 'text-teal-300' : 'text-slate-400'}`}>
                    {m.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="border-t border-slate-800/50 my-6"></div>

        {/* Binaural Frequency select */}
        <div className="space-y-3">
          <label className="text-xs font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-slate-400" /> Theta / Delta Binaural Beats
          </label>
          <div className="grid grid-cols-2 gap-3">
            {binauralList.map((b) => (
              <button
                key={b.id}
                onClick={() => setBinauralFreq(b.id)}
                className={`text-left p-3.5 rounded-xl border transition-all duration-300 relative ${
                  binauralFreq === b.id
                    ? 'bg-indigo-600/10 border-indigo-500 shadow-glow'
                    : 'bg-dark-800/40 border-slate-800/60 hover:bg-slate-800/30'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`font-semibold text-sm transition-colors ${binauralFreq === b.id ? 'text-indigo-300' : 'text-slate-300'}`}>
                    {b.label}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500 bg-dark-600 px-1.5 py-0.5 rounded border border-slate-800">
                    {b.freq}
                  </span>
                </div>
                <div className="text-[10px] text-slate-500 mt-1">{b.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-800/50 my-6"></div>

        {/* Session length */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
              <Timer className="w-3.5 h-3.5 text-slate-400" /> Target Session Length
            </label>
            <span className="text-sm font-bold text-indigo-400">{sessionLength} Minutes</span>
          </div>
          <div className="space-y-2">
            <input
              type="range"
              min="5"
              max="45"
              step="5"
              value={sessionLength}
              onChange={(e) => setSessionLength(parseInt(e.target.value))}
              className="w-full accent-indigo-500 bg-dark-600 h-1.5 rounded-lg appearance-none cursor-pointer border border-slate-800"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-medium">
              <span>5m</span>
              <span>15m</span>
              <span>25m</span>
              <span>35m</span>
              <span>45m</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
