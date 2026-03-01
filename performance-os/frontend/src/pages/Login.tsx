import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { User, Lock, Activity } from 'lucide-react';

export const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login, isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await axios.post('/api/v1/auth/token', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            login(response.data.access_token);
        } catch (err) {
            setError('Invalid credentials. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-wrapper">
            <div className="app-container flex-col items-center justify-center p-6 bg-[#0f121b]">
                <div className="w-full max-w-sm animate-fade-up flex flex-col items-center">

                    <h1 className="text-xl font-medium text-slate-300 mb-8 mt-4 text-center">Welcome to Performance Management System</h1>

                    {/* Glowing Logo representation */}
                    <div className="relative mb-12 flex items-center justify-center w-32 h-32 rounded-full border-2 border-transparent bg-gradient-to-tr from-[#00e5ff] to-[#b429f9] p-[2px]">
                        <div className="w-full h-full bg-[#0f121b] rounded-full flex items-center justify-center relative">
                            {/* Outer glow ring effect simulated by box-shadow */}
                            <div className="absolute inset-0 rounded-full shadow-[0_0_30px_rgba(0,229,255,0.4)] mix-blend-screen pointer-events-none"></div>
                            <Activity size={48} className="text-[#00e5ff]" />
                        </div>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 w-full bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl text-sm text-center">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
                        <div className="input-wrapper">
                            <input
                                type="email"
                                className="input"
                                placeholder="Employee ID or Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                            <User className="input-icon" size={20} />
                        </div>

                        <div className="input-wrapper mb-2">
                            <input
                                type="password"
                                className="input"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <Lock className="input-icon" size={20} />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary mt-4"
                            disabled={isLoading}
                        >
                            {isLoading ? <div className="loader"></div> : 'Secure Sign-In'}
                        </button>

                        <button type="button" className="text-slate-400 text-sm mt-4 hover:text-white transition-colors">
                            Forgot Password?
                        </button>
                    </form>

                    <div className="mt-8 text-center text-xs text-slate-500 p-4 rounded-xl border border-white/5 bg-[#1a1d27]/50 w-full">
                        <span className="block mb-1 font-medium text-slate-400">Demo Credentials</span>
                        admin@acme.com / password123
                    </div>
                </div>
            </div>
        </div>
    );
};
