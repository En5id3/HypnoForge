import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ScriptInput from './components/ScriptInput';
import CustomizationPanel from './components/CustomizationPanel';
import PlayerPreview from './components/PlayerPreview';
import Dashboard from './components/Dashboard';

export default function App() {
  const [activeView, setActiveView] = useState('forge');

  // Unified settings states
  const [prompt, setPrompt] = useState('');
  const [script, setScript] = useState('');
  const [style, setStyle] = useState('Ericksonian');
  const [voice, setVoice] = useState('deep_male');
  const [musicTheme, setMusicTheme] = useState('ocean');
  const [binauralFreq, setBinauralFreq] = useState('theta');
  const [sessionLength, setSessionLength] = useState(10);

  // Load a preset's parameters back into the editor
  const handleLoadSettings = (settings) => {
    setStyle(settings.style);
    setVoice(settings.voice);
    setMusicTheme(settings.music_theme);
    setBinauralFreq(settings.binaural_freq);
    setSessionLength(settings.session_length);
    setActiveView('forge');
  };

  return (
    <div className="flex min-h-screen bg-dark-950 text-slate-100 antialiased font-sans">
      {/* Decorative Background Pulsing Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full cosmic-glow-purple z-0 pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full cosmic-glow-teal z-0 pointer-events-none"></div>

      {/* Main Sidebar Navigation */}
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      {/* Main Panel Content */}
      <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto space-y-6 relative z-10">
        
        {/* Header Branding */}
        <header className="flex items-center justify-between border-b border-slate-800/40 pb-5">
          <div>
            <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
              {activeView === 'forge' && 'Forge Session Studio'}
              {activeView === 'dashboard' && 'Dashboard Analytics'}
              {activeView === 'presets' && 'Preset Library'}
            </h2>
            <p className="text-xs text-slate-500 font-medium mt-1 uppercase tracking-wider">
              {activeView === 'forge' && 'Craft layered suggestions with low-frequency waves'}
              {activeView === 'dashboard' && 'View generated packages, exports, and templates'}
              {activeView === 'presets' && 'Select preset structures to quick-start generations'}
            </p>
          </div>
          
          <div className="text-xs text-slate-400 bg-dark-900 border border-slate-800/80 px-4 py-2 rounded-xl flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></span>
            <span>Workspace Active: HypnoFaux</span>
          </div>
        </header>

        {/* View Routing */}
        <div className="py-2">
          {activeView === 'forge' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Left Column: Script writing & rewriting (Colspan 7) */}
              <div className="lg:col-span-7">
                <ScriptInput
                  prompt={prompt}
                  setPrompt={setPrompt}
                  script={script}
                  setScript={setScript}
                  style={style}
                  sessionLength={sessionLength}
                />
              </div>

              {/* Right Column: Custom settings & Player controls (Colspan 5) */}
              <div className="lg:col-span-5 space-y-6">
                <CustomizationPanel
                  style={style}
                  setStyle={setStyle}
                  voice={voice}
                  setVoice={setVoice}
                  musicTheme={musicTheme}
                  setMusicTheme={setMusicTheme}
                  binauralFreq={binauralFreq}
                  setBinauralFreq={setBinauralFreq}
                  sessionLength={sessionLength}
                  setSessionLength={setSessionLength}
                />
                
                <PlayerPreview
                  prompt={prompt}
                  script={script}
                  style={style}
                  voice={voice}
                  musicTheme={musicTheme}
                  binauralFreq={binauralFreq}
                  sessionLength={sessionLength}
                />
              </div>

            </div>
          )}

          {activeView === 'dashboard' && (
            <Dashboard onLoadSettings={handleLoadSettings} />
          )}

          {activeView === 'presets' && (
            <Dashboard onLoadSettings={handleLoadSettings} />
          )}
        </div>

      </main>
    </div>
  );
}
