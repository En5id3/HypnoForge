import React from 'react';
import { Flame, LayoutDashboard, Disc, Settings, Library, Sparkles } from 'lucide-react';

export default function Sidebar({ activeView, setActiveView }) {
  const menuItems = [
    { id: 'forge', label: 'Forge Session', icon: Flame },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'presets', label: 'Preset Templates', icon: Disc },
  ];

  return (
    <aside className="w-72 bg-dark-900 border-r border-slate-800/60 p-6 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div className="space-y-8">
        {/* Branding Logo */}
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600/20 p-2.5 rounded-xl border border-indigo-500/30 shadow-glow">
            <Flame className="w-6 h-6 text-indigo-400 fill-indigo-500/10" />
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-wide bg-gradient-to-r from-indigo-200 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              HYPNOFORGE
            </h1>
            <p className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">
              Hypnosis Content Factory
            </p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 relative group ${
                  isActive
                    ? 'text-slate-100 bg-indigo-600/15 border-l-2 border-indigo-500 shadow-glow'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/30 border-l-2 border-transparent'
                }`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${
                  isActive ? 'text-indigo-400' : 'text-slate-400'
                }`} />
                <span>{item.label}</span>
                
                {isActive && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-indigo-400 rounded-full animate-pulse"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Decorative System Health / Status info */}
      <div className="bg-dark-800/80 rounded-xl p-4 border border-slate-800/50 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">Engine Mode</span>
          <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></span>
            Local Async
          </span>
        </div>
        <div className="h-[2px] bg-slate-800 rounded-full overflow-hidden">
          <div className="w-full h-full bg-gradient-to-r from-indigo-500 to-purple-500"></div>
        </div>
        <div className="text-[10px] text-slate-500 leading-relaxed">
          HypnoForge Engine v1.0.0. Layered mixing via FFmpeg is fully optimized.
        </div>
      </div>
    </aside>
  );
}
