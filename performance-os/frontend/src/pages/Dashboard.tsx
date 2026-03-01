import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Disc, ChevronRight, TrendingUp } from 'lucide-react';

export const Dashboard: React.FC = () => {
    // Removed unused goalsCount
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                await axios.get('/api/v1/goals/');
                // Removed setGoalsCount
            } catch (err) {
                console.error("Failed to load goals", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="loader"></div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10 animate-fade-up min-h-[101dvh]">

            <header className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white">Goal Dashboard 2.0</h1>
                    <p className="text-slate-400 mt-1">Overview of your current progress and pulse</p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column: Progress */}
                <div className="lg:col-span-5 xl:col-span-4">
                    {/* Circular Progress Section */}
                    <div className="glass-card flex flex-col items-center justify-center py-10 relative overflow-hidden lg:h-full">
                        {/* Background glow behind circle */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-[#00e5ff]/20 rounded-full blur-[60px] pointer-events-none"></div>

                        <div className="relative w-48 h-48 mb-4">
                            <svg viewBox="0 0 36 36" className="circular-chart text-[#00e5ff] w-full h-full drop-shadow-[0_0_15px_rgba(0,229,255,0.6)]">
                                <path className="circle-bg"
                                    d="M18 2.0845
                                  a 15.9155 15.9155 0 0 1 0 31.831
                                  a 15.9155 15.9155 0 0 1 0 -31.831"
                                />
                                <path className="circle"
                                    strokeDasharray="75, 100"
                                    stroke="url(#gradient)"
                                    d="M18 2.0845
                                  a 15.9155 15.9155 0 0 1 0 31.831
                                  a 15.9155 15.9155 0 0 1 0 -31.831"
                                />
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#0cebeb" />
                                        <stop offset="50%" stopColor="#20e3b2" />
                                        <stop offset="100%" stopColor="#29ffc6" />
                                    </linearGradient>
                                </defs>
                            </svg>

                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#00e5ff] to-[#29ffc6]">75%</span>
                                <span className="text-sm text-slate-400">Complete</span>
                            </div>
                        </div>

                        {/* Segments Mockup */}
                        <div className="flex gap-2 mt-4 w-full px-6 justify-between">
                            {[1, 2, 3, 4, 5, 6].map(i => (
                                <div key={i} className={`h-2 rounded-full flex-1 ${i <= 4 ? 'bg-[#00e5ff]' : 'bg-slate-700/50'}`}></div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Weekly Pulse */}
                <div className="lg:col-span-7 xl:col-span-8">
                    <div className="glass-card lg:h-full">
                        <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
                            <TrendingUp size={20} className="text-[#00e5ff]" />
                            Weekly Pulse
                        </h3>

                        <div className="flex flex-col gap-3">
                            <div className="p-4 rounded-xl bg-[#1a1d27] border border-white/5 flex flex-col sm:flex-row sm:items-center gap-4 hover:border-[#0cebeb]/50 transition-colors cursor-pointer group">
                                <div className="p-2.5 rounded-lg bg-[#0cebeb]/10 text-[#0cebeb] shrink-0 w-fit">
                                    <Disc size={20} />
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-slate-200">Launch Feature X</p>
                                    <p className="text-sm text-slate-500 mt-0.5">Development objective</p>
                                </div>
                                <div className="shrink-0 text-right">
                                    <div className="text-lg font-bold text-[#0cebeb]">0%</div>
                                    <div className="text-xs text-slate-500 uppercase tracking-wider">Progress</div>
                                </div>
                            </div>

                            <div className="p-4 rounded-xl bg-[#1a1d27] border border-white/5 flex flex-col sm:flex-row sm:items-center gap-4 hover:border-[#f59e0b]/50 transition-colors cursor-pointer group">
                                <div className="p-2.5 rounded-lg bg-[#f59e0b]/10 text-[#f59e0b] shrink-0 w-fit">
                                    <Disc size={20} />
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-slate-200">Complete Certifications</p>
                                    <p className="text-sm text-slate-500 mt-0.5">Learning objective</p>
                                </div>
                                <div className="shrink-0 text-right">
                                    <div className="text-lg font-bold text-[#f59e0b]">55%</div>
                                    <div className="text-xs text-slate-500 uppercase tracking-wider">Progress</div>
                                </div>
                            </div>

                            <div className="p-4 rounded-xl bg-[#1a1d27] border border-[#ef4444]/30 shadow-[0_0_15px_rgba(239,68,68,0.1)] flex flex-col sm:flex-row sm:items-center gap-4 hover:border-[#ef4444]/50 transition-colors cursor-pointer group">
                                <div className="p-2.5 rounded-lg bg-[#ef4444]/10 text-[#ef4444] shrink-0 w-fit">
                                    <Disc size={20} />
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-[#ef4444]">Delegate Tasks</p>
                                    <p className="text-sm text-slate-500 mt-0.5">Management objective</p>
                                </div>
                                <div className="shrink-0 text-right">
                                    <div className="inline-block px-2.5 py-1 bg-[#ef4444]/20 text-[#ef4444] text-xs font-bold uppercase tracking-wider rounded-md">
                                        Overdue
                                    </div>
                                </div>
                            </div>

                            <div className="p-4 rounded-xl bg-[#1a1d27] border border-[#00e5ff]/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[#00e5ff]/5 transition-colors cursor-pointer group">
                                <div className="flex items-center gap-4">
                                    <div className="p-2.5 rounded-lg bg-[#00e5ff]/10 text-[#00e5ff] shrink-0 w-fit">
                                        <Disc size={20} />
                                    </div>
                                    <div>
                                        <p className="font-semibold text-[#00e5ff]">Mentor J. Doe</p>
                                        <p className="text-sm text-slate-500 mt-0.5">Team objective</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-1 text-sm font-medium text-[#00e5ff] group-hover:translate-x-1 transition-transform">
                                    Details <ChevronRight size={16} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
};
