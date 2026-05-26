import React, { useState, useEffect } from 'react';
import { Play, Star, Trash2, Calendar, FileText, Music, Video, Clock, CheckCircle2, ChevronRight, Bookmark } from 'lucide-react';

export default function Dashboard({ onLoadSettings }) {
  const [generations, setGenerations] = useState([]);
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [genRes, presetRes] = await Promise.all([
        fetch('/api/generations'),
        fetch('/api/presets')
      ]);

      if (!genRes.ok || !presetRes.ok) {
        throw new Error('Failed to load history data from backend.');
      }

      const genData = await genRes.json();
      const presetData = await presetRes.json();

      setGenerations(genData);
      setPresets(presetData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleToggleFavorite = async (id, currentVal) => {
    try {
      const response = await fetch(`/api/generations/${id}/favorite`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_favorite: !currentVal })
      });
      if (!response.ok) throw new Error();
      
      // Update local state
      setGenerations(prev => 
        prev.map(g => g.id === id ? { ...g, is_favorite: !currentVal } : g)
      );
    } catch (err) {
      console.error("Failed to toggle favorite", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this generation history?")) return;
    try {
      const response = await fetch(`/api/generations/${id}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error();
      
      // Update local state
      setGenerations(prev => prev.filter(g => g.id !== id));
    } catch (err) {
      console.error("Failed to delete generation", err);
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-8">
      {/* Overview stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-indigo-600/10 border border-indigo-500/25 rounded-xl text-indigo-400">
            <Music className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">Total Audio Sessions</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{generations.length}</div>
          </div>
        </div>
        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-purple-600/10 border border-purple-500/25 rounded-xl text-purple-400">
            <Star className="w-6 h-6 fill-purple-400/10" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">Favorites</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">
              {generations.filter(g => g.is_favorite).length}
            </div>
          </div>
        </div>
        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-teal-600/10 border border-teal-500/25 rounded-xl text-teal-400">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">Total Session Time</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">
              {generations.reduce((acc, curr) => acc + (curr.status === 'completed' ? curr.session_length : 0), 0)}m
            </div>
          </div>
        </div>
      </div>

      {/* Preset Templates */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-400 tracking-wider uppercase flex items-center gap-2">
          <Bookmark className="w-4 h-4 text-indigo-400" /> Quick-Load Presets
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {presets.map((preset) => (
            <div 
              key={preset.id} 
              className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/30 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                <h4 className="font-bold text-sm text-slate-200">{preset.name}</h4>
                <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">{preset.description}</p>
                
                {/* Meta details */}
                <div className="flex flex-wrap gap-2 mt-4">
                  <span className="text-[9px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded font-medium">
                    {preset.style}
                  </span>
                  <span className="text-[9px] bg-teal-500/10 text-teal-300 border border-teal-500/20 px-2 py-0.5 rounded font-medium capitalize">
                    {preset.music_theme.replace('_', ' ')}
                  </span>
                  <span className="text-[9px] bg-purple-500/10 text-purple-300 border border-purple-500/20 px-2 py-0.5 rounded font-mono">
                    {preset.binaural_freq}
                  </span>
                </div>
              </div>
              <button 
                onClick={() => onLoadSettings(preset)}
                className="w-full mt-4 flex items-center justify-center gap-1 bg-indigo-600/15 hover:bg-indigo-600 border border-indigo-500/20 hover:border-indigo-500 text-indigo-300 hover:text-slate-100 text-xs font-semibold py-2 rounded-xl transition-all"
              >
                <span>Load Template Settings</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Generation History List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-400 tracking-wider uppercase">Session History Logs</h3>
        {loading ? (
          <div className="text-center py-12 text-slate-500 text-sm">Loading history...</div>
        ) : generations.length === 0 ? (
          <div className="glass-panel p-8 rounded-2xl text-center py-12 text-slate-500 text-sm">
            No session generations recorded yet. Go to 'Forge Session' to create your first package.
          </div>
        ) : (
          <div className="space-y-3">
            {generations.map((gen) => (
              <div 
                key={gen.id}
                className="glass-panel p-5 rounded-2xl border border-slate-800/80 hover:border-slate-800 transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Info block */}
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-bold text-sm text-slate-200 truncate max-w-xs">{gen.prompt}</h4>
                    <span className={`text-[10px] px-2 py-0.5 rounded border ${
                      gen.status === 'completed' 
                        ? 'bg-teal-500/10 border-teal-500/20 text-teal-400' 
                        : gen.status === 'failed' 
                        ? 'bg-red-500/10 border-red-500/20 text-red-400' 
                        : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400 animate-pulse'
                    }`}>
                      {gen.status}
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-400">
                    <span className="flex items-center gap-1 text-[11px]">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      {formatDate(gen.created_at)}
                    </span>
                    <span className="flex items-center gap-1 text-[11px]">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      {gen.session_length} min
                    </span>
                    <span className="text-[11px] text-slate-500 font-medium font-mono bg-dark-600 px-1.5 py-0.5 rounded border border-slate-800">
                      {gen.style} // {gen.voice.replace('_', ' ')} // {gen.binaural_freq}
                    </span>
                  </div>
                </div>

                {/* Media Links / Actions block */}
                <div className="flex items-center gap-3 self-end md:self-center">
                  {gen.status === 'completed' && (
                    <div className="flex items-center gap-2">
                      {gen.audio_url && (
                        <a 
                          href={gen.audio_url} 
                          download
                          title="Download MP3"
                          className="p-2 bg-dark-600 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-800 transition-colors"
                        >
                          <Music className="w-4 h-4 text-teal-400" />
                        </a>
                      )}
                      {gen.video_url && (
                        <a 
                          href={gen.video_url} 
                          download
                          title="Download MP4"
                          className="p-2 bg-dark-600 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-800 transition-colors"
                        >
                          <Video className="w-4 h-4 text-indigo-400" />
                        </a>
                      )}
                    </div>
                  )}
                  
                  <div className="h-5 w-[1px] bg-slate-800 hidden md:block mx-1"></div>

                  <button
                    onClick={() => handleToggleFavorite(gen.id, gen.is_favorite)}
                    className={`p-2 rounded-xl border border-slate-800/80 transition-colors ${
                      gen.is_favorite 
                        ? 'bg-purple-600/15 text-purple-400 border-purple-500/25' 
                        : 'bg-dark-600 hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Star className={`w-4 h-4 ${gen.is_favorite ? 'fill-purple-400' : ''}`} />
                  </button>

                  <button
                    onClick={() => handleDelete(gen.id)}
                    className="p-2 bg-dark-600 hover:bg-red-950/20 text-slate-400 hover:text-red-400 rounded-xl border border-slate-800/80 hover:border-red-500/20 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
