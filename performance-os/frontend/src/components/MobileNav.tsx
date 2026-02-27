import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard,
    Target,
    MessageSquare,
    Home,
    LogOut
} from 'lucide-react';

export const MobileNav: React.FC = () => {
    const { isAuthenticated, logout } = useAuth();

    if (!isAuthenticated) return null;

    const NavItem = ({ to, icon }: { to: string, icon: React.ReactNode }) => (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex flex-col items-center justify-center w-full h-full gap-1 transition-colors ${isActive
                    ? 'text-white'
                    : 'text-[#6b7280] hover:text-slate-300'
                }`
            }
        >
            {icon}
        </NavLink>
    );

    return (
        <nav
            className="lg:hidden fixed bottom-0 inset-x-0 mx-auto max-w-md flex items-center justify-around z-50 px-2 bottom-nav"
            style={{
                paddingBottom: 'var(--sab)',
                height: 'calc(70px + var(--sab))'
            }}
        >
            <NavItem to="/dashboard" icon={<Home size={24} />} />
            <NavItem to="/goals" icon={<Target size={24} />} />

            {/* Center floating action or primary button approach */}
            <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center bg-[#1a1d27] -mt-4 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                <LayoutDashboard size={24} className="text-[#00e5ff]" />
            </div>

            <NavItem to="/feedback" icon={<MessageSquare size={24} />} />

            <button
                onClick={logout}
                className="flex flex-col items-center justify-center w-full h-full gap-1 transition-colors text-[#6b7280] hover:text-rose-400"
            >
                <LogOut size={24} />
            </button>
        </nav>
    );
};
