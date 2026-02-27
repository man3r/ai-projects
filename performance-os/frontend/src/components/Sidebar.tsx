import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    Activity,
    Target,
    MessageSquare,
    Settings,
    LogOut,
    Users
} from 'lucide-react';

export const Sidebar: React.FC = () => {
    const { user, logout } = useAuth();

    if (!user) return null;

    const NavItem = ({ to, icon, label }: { to: string, icon: React.ReactNode, label: string }) => (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex items-center gap-4 px-6 py-4 transition-colors ${isActive
                    ? 'text-white border-l-2 border-[#00e5ff] bg-gradient-to-r from-[#00e5ff]/10 to-transparent'
                    : 'text-[#6b7280] hover:text-slate-300 hover:bg-white/5'
                }`
            }
        >
            {icon}
            <span className="font-medium">{label}</span>
        </NavLink>
    );

    return (
        <aside className="w-full flex flex-col h-full bg-[#0f121b]">
            <div className="p-8 pb-4 flex items-center gap-3">
                {/* Logo mark */}
                <div className="w-8 h-8 rounded-full border border-transparent bg-gradient-to-tr from-[#00e5ff] to-[#b429f9] p-[1px] shadow-[0_0_15px_rgba(0,229,255,0.3)]">
                    <div className="w-full h-full bg-[#0f121b] rounded-full flex items-center justify-center">
                        <Activity size={16} className="text-[#00e5ff]" />
                    </div>
                </div>
                <h1 className="text-xl font-bold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#b429f9]">
                    Performance.os
                </h1>
            </div>
            <div className="px-8 py-6 mb-2">
                <div className="glass-card !p-4 flex items-center gap-4 bg-[#1a1d27]/50 border-white/5">
                    <div className="w-12 h-12 rounded-full border-2 border-[#00e5ff]/50 flex items-center justify-center overflow-hidden bg-slate-800 shadow-[0_0_10px_rgba(0,229,255,0.2)]">
                        <span className="text-[#00e5ff] font-bold text-lg">{user.sub.charAt(0).toUpperCase()}</span>
                    </div>
                    <div className="overflow-hidden flex-1">
                        <p className="text-sm font-medium text-slate-100 truncate">{user.sub}</p>
                        <p className="text-xs text-[#b429f9] truncate">{user.role}</p>
                    </div>
                </div>
            </div>

            <div className="px-8 mt-2 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">
                Main Menu
            </div>

            <nav className="flex-1 flex flex-col">
                <NavItem to="/dashboard" icon={<Activity size={22} />} label="Dashboard" />
                <NavItem to="/goals" icon={<Target size={22} />} label="My Goals" />
                <NavItem to="/reviews" icon={<Users size={22} />} label="Reviews" />
                <NavItem to="/feedback" icon={<MessageSquare size={22} />} label="Feedback" />

                <div className="px-8 mt-10 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">
                    Preferences
                </div>
                <NavItem to="/settings" icon={<Settings size={22} />} label="Settings" />
            </nav>

            <div className="p-8 pt-4">
                <button
                    onClick={logout}
                    className="w-full flex items-center justify-center gap-3 px-6 py-4 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors border border-transparent hover:border-white/10"
                >
                    <LogOut size={20} />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </aside>
    );
};
