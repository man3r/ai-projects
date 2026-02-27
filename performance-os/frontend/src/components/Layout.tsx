import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';
import { useAuth } from '../context/AuthContext';

export const Layout: React.FC = () => {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="lg:app-wrapper app-screen-wrapper">
            <div className="app-container lg:rounded-[2rem] rounded-none lg:border border-0">
                {/* Desktop Sidebar */}
                <div className="hidden lg:block w-[280px] shrink-0 border-r border-[#1a1d27] bg-[#0f121b]">
                    <Sidebar />
                </div>

                <main className="main-content relative overflow-y-auto">
                    {/* Simplified Mobile Header */}
                    <header
                        className="h-[70px] flex items-center justify-center sticky top-0 bg-transparent z-30 lg:hidden shrink-0"
                    >
                        <h1 className="text-xl font-semibold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#b429f9]">
                            Performance.os
                        </h1>
                    </header>

                    <div className="flex-1 w-full flex flex-col p-4 md:p-8">
                        <Outlet />
                    </div>
                </main>

                {/* Mobile Bottom Navigation */}
                <MobileNav />
            </div>
        </div>
    );
};
