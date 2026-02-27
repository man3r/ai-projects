import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Target, Plus } from 'lucide-react';
import type { Goal } from '../types/Goal';
import { CreateGoalModal } from '../components/CreateGoalModal';

export const Goals: React.FC = () => {
    const [goals, setGoals] = useState<Goal[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const fetchGoals = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('/api/v1/goals/');
            setGoals(response.data);
        } catch (err) {
            console.error("Failed to load goals", err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchGoals();
    }, [fetchGoals]);

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="loader"></div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10 animate-fade-up min-h-[101dvh]">
            <header className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#b429f9]">
                        My Goals
                    </h1>
                    <p className="text-slate-400 mt-1">Manage your active objectives and results</p>
                </div>
                <button className="btn btn-primary !w-auto !px-4" onClick={() => setIsCreateModalOpen(true)}>
                    <Plus size={20} />
                    <span className="hidden sm:inline">New Goal</span>
                </button>
            </header>

            {goals.length === 0 ? (
                <div className="glass-card flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-16 h-16 rounded-full bg-[#00e5ff]/10 text-[#00e5ff] flex items-center justify-center mb-4">
                        <Target size={32} />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-200 mb-2">No Active Goals</h3>
                    <p className="text-slate-400 max-w-md">
                        You don't have any focus areas or objectives assigned yet.
                        Create a new goal to start tracking your performance.
                    </p>
                    <button className="btn btn-secondary mt-6 !w-auto" onClick={() => setIsCreateModalOpen(true)}>
                        Get Started
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {goals.map(goal => (
                        <div key={goal.id} className="glass-card flex flex-col h-full group hover:border-[#00e5ff]/30 cursor-pointer transition-colors relative overflow-hidden">
                            {/* Top accent line */}
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#00e5ff] to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

                            <div className="flex justify-between items-start mb-4 gap-4">
                                <div className="flex-1">
                                    {goal.tier_level === 1 && <span className="text-xs font-semibold text-[#b429f9] uppercase tracking-wider mb-1 block">Focus Area</span>}
                                    {goal.tier_level === 2 && <span className="text-xs font-semibold text-[#00e5ff] uppercase tracking-wider mb-1 block">Objective</span>}
                                    {goal.tier_level === 3 && <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1 block">Measure</span>}
                                    <h3 className="text-lg font-medium text-slate-200 line-clamp-2 leading-tight">{goal.title}</h3>
                                </div>
                                <div className="text-right shrink-0">
                                    <span className="text-2xl font-bold text-slate-100">
                                        {goal.current_value || 0}
                                    </span>
                                    <span className="text-xs text-slate-400 block mt-0.5">
                                        / {goal.target_value !== null ? goal.target_value : '-'} {goal.unit || ''}
                                    </span>
                                </div>
                            </div>

                            {goal.description && (
                                <p className="text-sm text-slate-400 line-clamp-3 mb-6 flex-1">
                                    {goal.description}
                                </p>
                            )}

                            {goal.target_value && (
                                <div className="w-full h-1.5 bg-[#1a1d27] rounded-full overflow-hidden mt-auto">
                                    <div
                                        className="h-full bg-gradient-to-r from-[#00e5ff] to-[#20e3b2]"
                                        style={{ width: `${Math.min(100, Math.max(0, ((goal.current_value || 0) / goal.target_value) * 100))}%` }}
                                    ></div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <CreateGoalModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={() => {
                    setIsCreateModalOpen(false);
                    fetchGoals();
                }}
            />
        </div>
    );
};
