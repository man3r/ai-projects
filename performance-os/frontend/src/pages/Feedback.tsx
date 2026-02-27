import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { MessageSquarePlus, Award, TrendingUp, User as UserIcon } from 'lucide-react';
import type { Feedback, UserResponse } from '../types/Feedback';
import { CreateFeedbackModal } from '../components/CreateFeedbackModal';
// Removed useAuth import
export const FeedbackPage: React.FC = () => {
    // Removed unused currentUser
    const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
    const [usersDict, setUsersDict] = useState<Record<number, UserResponse>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setIsLoading(true);
            const [feedbackRes, usersRes] = await Promise.all([
                axios.get('/api/v1/feedback/'),
                axios.get('/api/v1/auth/users')
            ]);

            setFeedbacks(feedbackRes.data.reverse()); // Show newest first

            const uDict: Record<number, UserResponse> = {};
            usersRes.data.forEach((u: UserResponse) => {
                uDict[u.id] = u;
            });
            setUsersDict(uDict);

        } catch (err) {
            console.error("Failed to load feedback data", err);
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

    return (
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10 animate-fade-up min-h-[101dvh]">
            <header className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#b429f9]">
                        Continuous Feedback
                    </h1>
                    <p className="text-slate-400 mt-1">Recognize peers and share constructive thoughts</p>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="btn btn-primary !w-auto !px-4 shrink-0"
                >
                    <MessageSquarePlus size={20} />
                    <span className="hidden sm:inline">Give Feedback</span>
                    <span className="sm:hidden">Give</span>
                </button>
            </header>

            {feedbacks.length === 0 ? (
                <div className="glass-card flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-16 h-16 rounded-full bg-[#b429f9]/10 text-[#b429f9] flex items-center justify-center mb-4">
                        <Award size={32} />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-200 mb-2">No Feedback Yet</h3>
                    <p className="text-slate-400 max-w-md">
                        The timeline is empty. Be the first to recognize a colleague's hard work or share a moment of brilliance!
                    </p>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="btn btn-secondary mt-6 !w-auto border-[#b429f9]/30 text-[#b429f9] hover:bg-[#b429f9]/10"
                    >
                        Give Kudos
                    </button>
                </div>
            ) : (
                <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
                    {feedbacks.map(item => {
                        const sender = usersDict[item.sender_id];
                        const receiver = usersDict[item.receiver_id];
                        const isKudo = item.feedback_type === 'kudo';

                        return (
                            <div key={item.id} className="break-inside-avoid relative glass-card group hover:border-white/10 transition-colors">
                                {/* Top Accent Line */}
                                <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${isKudo ? 'from-emerald-400' : 'from-[#b429f9]'} to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-t-lg`}></div>

                                <div className="flex items-start justify-between mb-3 gap-2">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 shrink-0">
                                            <UserIcon size={20} />
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-slate-200">
                                                <span className={`${isKudo ? 'text-emerald-400' : 'text-[#b429f9]'}`}>{sender?.full_name || 'Unknown'}</span>
                                                <span className="text-slate-500 mx-2">→</span>
                                                <span className="text-white">{receiver?.full_name || 'Unknown'}</span>
                                            </div>
                                            <span className="text-xs text-slate-500 block mt-0.5">
                                                {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                    </div>

                                    <div className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 shrink-0 ${isKudo ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20' : 'bg-[#b429f9]/10 text-[#b429f9] border border-[#b429f9]/20'}`}>
                                        {isKudo ? <Award size={12} /> : <TrendingUp size={12} />}
                                        {isKudo ? 'Kudos' : 'Constructive'}
                                    </div>
                                </div>

                                <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap py-2">
                                    "{item.message}"
                                </p>
                            </div>
                        );
                    })}
                </div>
            )}

            <CreateFeedbackModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={() => {
                    setIsCreateModalOpen(false);
                    fetchData();
                }}
            />
        </div>
    );
};
