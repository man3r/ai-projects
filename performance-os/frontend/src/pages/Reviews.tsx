import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { FileText, Calendar, CheckCircle2, ChevronRight } from 'lucide-react';
import type { ReviewCycle, Review } from '../types/Review';
import type { UserResponse } from '../types/Feedback';
import { SelfReflectionModal } from '../components/SelfReflectionModal';
import { ManagerAssessmentModal } from '../components/ManagerAssessmentModal';
import { useAuth } from '../context/AuthContext';

export const Reviews: React.FC = () => {
    const { user: currentUser } = useAuth();
    const [cycles, setCycles] = useState<ReviewCycle[]>([]);
    const [myReviews, setMyReviews] = useState<Review[]>([]);
    const [usersDict, setUsersDict] = useState<Record<number, UserResponse>>({});
    const [isLoading, setIsLoading] = useState(true);

    const [selectedReview, setSelectedReview] = useState<Review | null>(null);
    const [isReflectionModalOpen, setIsReflectionModalOpen] = useState(false);
    const [isManagerModalOpen, setIsManagerModalOpen] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setIsLoading(true);
            const [cyclesRes, reviewsRes, usersRes] = await Promise.all([
                axios.get('/api/v1/reviews/cycles'),
                axios.get('/api/v1/reviews/'),
                axios.get('/api/v1/auth/users')
            ]);

            setCycles(cyclesRes.data);
            setMyReviews(reviewsRes.data);

            const uDict: Record<number, UserResponse> = {};
            usersRes.data.forEach((u: UserResponse) => {
                uDict[u.id] = u;
            });
            setUsersDict(uDict);

        } catch (err) {
            console.error("Failed to load review data", err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="loader"></div>
            </div>
        );
    }

    const activeCycles = cycles.filter(c => c.status === 'active');

    return (
        <div className="w-full max-w-7xl mx-auto pb-10 animate-fade-up min-h-[101dvh]">
            <header className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#b429f9]">
                        Performance Reviews
                    </h1>
                    <p className="text-slate-400 mt-1">Manage your self-reflections and active cycles</p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Active Cycles Column */}
                <div className="lg:col-span-1 border-r border-white/5 pr-0 lg:pr-6">
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4">Active Cycles</h2>

                    {activeCycles.length === 0 ? (
                        <div className="glass-card p-6 text-center">
                            <Calendar className="mx-auto text-slate-600 mb-3" size={24} />
                            <p className="text-sm text-slate-400">No active review cycles.</p>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-3">
                            {activeCycles.map(cycle => (
                                <div key={cycle.id} className="glass-card p-4 hover:border-white/10 transition-colors cursor-pointer group">
                                    <h3 className="font-semibold text-slate-200 group-hover:text-[#00e5ff] transition-colors">{cycle.name}</h3>
                                    <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
                                        <div className="flex items-center gap-1.5">
                                            <Calendar size={14} />
                                            {new Date(cycle.start_date).toLocaleDateString()} - {new Date(cycle.end_date).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <div className="mt-3 inline-block px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-[#b429f9]/20 text-[#b429f9]">
                                        {cycle.status}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* My Action Items Column */}
                <div className="lg:col-span-2">
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4">My Assessments</h2>

                    {myReviews.length === 0 ? (
                        <div className="glass-card flex flex-col items-center justify-center p-12 text-center border-dashed border-white/10">
                            <FileText className="text-slate-600 mb-4" size={32} />
                            <h3 className="text-lg font-medium text-slate-300">You're all caught up!</h3>
                            <p className="text-sm text-slate-500 mt-2 max-w-sm">
                                You do not have any pending self-reflections or assessments at this time.
                            </p>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-4">
                            {myReviews.map(review => {
                                const cycle = cycles.find(c => c.id === review.cycle_id);
                                const isCompleted = review.status === 'calibrated' || review.status === 'finished';

                                return (
                                    <div
                                        key={review.id}
                                        onClick={() => {
                                            setSelectedReview(review);
                                            setIsReflectionModalOpen(true);
                                        }}
                                        className="glass-card p-5 flex items-center justify-between group cursor-pointer hover:border-white/10 transition-colors"
                                    >
                                        <div>
                                            <div className="flex items-center gap-3 mb-1">
                                                <h3 className="font-semibold text-slate-200">Self Reflection</h3>
                                                {isCompleted ? (
                                                    <span className="flex items-center gap-1 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">
                                                        <CheckCircle2 size={12} /> Completed
                                                    </span>
                                                ) : (
                                                    <span className="flex items-center gap-1 text-xs font-medium text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-full">
                                                        Action Required
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-slate-400">{cycle?.name}</p>
                                        </div>

                                        <div className="w-10 h-10 rounded-full bg-slate-800/50 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-[#b429f9]/20 transition-all">
                                            <ChevronRight size={20} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Team Assessments Column (Only for Managers/Admins) */}
                {(currentUser?.role === 'Manager' || currentUser?.role === 'Tenant Admin' || currentUser?.role === 'Platform Admin') && (
                    <div className="lg:col-span-3 mt-8">
                        <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Team Assessments</h2>
                            <span className="text-xs text-slate-400">{myReviews.filter(r => r.employee_id !== currentUser?.user_id).length} Pending</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {myReviews.filter(r => r.employee_id !== currentUser?.user_id).map(review => {
                                const cycle = cycles.find(c => c.id === review.cycle_id);
                                const employee = usersDict[review.employee_id];

                                return (
                                    <div
                                        key={review.id}
                                        onClick={() => {
                                            setSelectedReview(review);
                                            setIsManagerModalOpen(true);
                                        }}
                                        className="glass-card p-5 group cursor-pointer hover:border-white/10 transition-colors border-l-2 border-l-[#b429f9]"
                                    >
                                        <div className="flex justify-between items-start mb-3">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 shrink-0">
                                                    {employee?.full_name.charAt(0)}
                                                </div>
                                                <div>
                                                    <h3 className="font-semibold text-slate-200 text-sm">{employee?.full_name || 'Employee'}</h3>
                                                    <p className="text-xs text-slate-500">{employee?.job_title || 'No Title'}</p>
                                                </div>
                                            </div>
                                            <span className="flex items-center gap-1 text-[10px] uppercase font-bold text-[#b429f9] bg-[#b429f9]/10 px-2 py-0.5 rounded-full">
                                                Review
                                            </span>
                                        </div>
                                        <div className="text-xs text-slate-400 mt-2">
                                            <span className="font-medium text-slate-300">Cycle:</span> {cycle?.name}
                                        </div>
                                    </div>
                                );
                            })}
                            {myReviews.filter(r => r.employee_id !== currentUser?.user_id).length === 0 && (
                                <div className="col-span-full text-center py-8 text-slate-500 text-sm glass-card border-dashed">
                                    No team assessments pending for your review.
                                </div>
                            )}
                        </div>
                    </div>
                )}

            </div>

            <SelfReflectionModal
                isOpen={isReflectionModalOpen}
                onClose={() => setIsReflectionModalOpen(false)}
                onSuccess={() => {
                    setIsReflectionModalOpen(false);
                    fetchData();
                }}
                review={selectedReview}
                cycleName={cycles.find(c => c.id === selectedReview?.cycle_id)?.name || 'Review Cycle'}
            />

            <ManagerAssessmentModal
                isOpen={isManagerModalOpen}
                onClose={() => setIsManagerModalOpen(false)}
                onSuccess={() => {
                    setIsManagerModalOpen(false);
                    fetchData();
                }}
                review={selectedReview}
                employee={selectedReview ? usersDict[selectedReview.employee_id] : null}
                cycleName={cycles.find(c => c.id === selectedReview?.cycle_id)?.name || 'Review Cycle'}
            />
        </div>
    );
};
