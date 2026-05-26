import React, { useState } from 'react';
import { Sparkles, Edit3, Wand2, RefreshCw, AlertCircle } from 'lucide-react';

export default function ScriptInput({ 
  prompt, 
  setPrompt, 
  script, 
  setScript, 
  style, 
  sessionLength 
}) {
  const [isRewriting, setIsRewriting] = useState(false);
  const [error, setError] = useState(null);

  const samplePrompts = [
    "Deep sleep induction to cure insomnia",
    "Relieving performance anxiety and social panic",
    "Building unbreakable self-worth and confidence",
    "Deep relaxation for self-healing and stress release",
  ];

  const handleRewrite = async () => {
    if (!prompt.trim()) return;
    setIsRewriting(true);
    setError(null);
    try {
      const response = await fetch('/api/rewrite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          style,
          session_length: sessionLength
        })
      });
      if (!response.ok) {
        throw new Error('Failed to rewrite script. Please check connection.');
      }
      const data = await response.json();
      setScript(data.rewritten_script);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRewriting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Prompt Card */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold tracking-wider text-slate-300 uppercase flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            1. Describe the Session Goal / Topic
          </label>
        </div>

        <div className="space-y-3">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Deep sleep hypnosis for falling asleep fast, releasing anxiety, or a script to manifest confidence..."
            className="w-full h-24 glass-input rounded-xl p-4 text-sm text-slate-200 resize-none font-sans"
          />

          {/* Quick presets */}
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-[11px] text-slate-500 font-semibold tracking-widest uppercase">Quick Samples:</span>
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => setPrompt(p)}
                className="text-[11px] bg-dark-600 hover:bg-indigo-600/20 hover:text-indigo-300 text-slate-400 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-950/30 border border-red-500/20 text-red-300 text-xs p-3 rounded-xl flex items-center gap-2.5">
            <AlertCircle className="w-4.5 h-4.5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <button
          onClick={handleRewrite}
          disabled={isRewriting || !prompt.trim()}
          className="w-full flex items-center justify-center gap-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:hover:from-indigo-600 disabled:hover:to-purple-600 text-slate-100 font-semibold text-sm py-3 px-5 rounded-xl border border-indigo-500/20 shadow-glow transition-all duration-300"
        >
          {isRewriting ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-indigo-300" />
              <span>Forging Hypnotic Script...</span>
            </>
          ) : (
            <>
              <Wand2 className="w-4 h-4 text-indigo-200" />
              <span>Forge Script with AI</span>
            </>
          )}
        </button>
      </div>

      {/* Script Editor Card */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold tracking-wider text-slate-300 uppercase flex items-center gap-2">
            <Edit3 className="w-4 h-4 text-purple-400" />
            2. Hypnotic Script Editor
          </label>
          <span className="text-[10px] bg-purple-500/10 text-purple-300 border border-purple-500/20 px-2.5 py-1 rounded-full font-mono">
            Interactive Editor
          </span>
        </div>

        <div className="relative">
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="The AI rewriter will output the hypnosis script here, or you can write/paste your own custom clinical script directly. Add timing anchors like [speed:0.85] or [pause:3] to fine-tune pauses."
            className="w-full h-80 glass-input rounded-xl p-4 text-sm font-mono text-indigo-200 resize-none leading-relaxed"
          />
        </div>

        <div className="p-3 bg-dark-800/80 rounded-xl border border-slate-800/40 text-[11px] text-slate-400 leading-normal flex items-start gap-2.5">
          <AlertCircle className="w-4.5 h-4.5 shrink-0 text-indigo-400 mt-0.5" />
          <div>
            <span className="font-semibold text-indigo-300">Pacing Tip:</span> You can insert custom pacing triggers manually anywhere in the text:
            <span className="bg-dark-600 px-1.5 py-0.5 rounded font-mono text-purple-300 mx-1 border border-slate-800">[pause:3]</span> to create a 3-second breathing space, or
            <span className="bg-dark-600 px-1.5 py-0.5 rounded font-mono text-indigo-300 mx-1 border border-slate-800">[speed:0.85]</span> to slow down the speed for deepeners.
          </div>
        </div>
      </div>
    </div>
  );
}
