import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Send, Rocket, Users, Lightbulb, Zap, Target, MessageCircle, User as UserIcon } from 'lucide-react';
import type { Review } from '../types/Review';
import type { UserResponse } from '../types/Feedback';

interface ManagerAssessmentModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    review: Review | null;
    employee: UserResponse | null;
    cycleName: string;
}

const STRENGTHS = [
    { id: 'problem_solver', label: 'Problem Solver', icon: Rocket },
    { id: 'team_player', label: 'Team Player', icon: Users },
    { id: 'innovative', label: 'Innovative', icon: Lightbulb },
    { id: 'high_velocity', label: 'High Velocity', icon: Zap },
    { id: 'strategic_thinker', label: 'Strategic Thinker', icon: Target },
    { id: 'comm_master', label: 'Comm. Master', icon: MessageCircle },
];

export const ManagerAssessmentModal: React.FC<ManagerAssessmentModalProps> = ({
    isOpen, onClose, onSuccess, review, employee, cycleName
}) => {
    const [assessmentText, setAssessmentText] = useState('');
    const [selectedStrengths, setSelectedStrengths] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (review) {
            // If we're editing an existing assessment, we might need to parse standard text
            // For now, assume it's blank or just load the whole thing into the textarea
            setAssessmentText(review.manager_assessment || '');
            setSelectedStrengths([]);
        }
    }, [review]);

    const toggleStrength = (id: string) => {
        setSelectedStrengths(prev => {
            if (prev.includes(id)) return prev.filter(s => s !== id);
            if (prev.length >= 3) return prev;
            return [...prev, id];
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!review) return;

        setIsLoading(true);

        try {
            // Append strengths to the assessment text to fit the schema
            const strengthsLabels = selectedStrengths.map(id => STRENGTHS.find(s => s.id === id)?.label).join(', ');
            let finalAssessment = assessmentText;
            if (strengthsLabels) {
                finalAssessment += `\n\nKey Strengths: ${strengthsLabels}`;
            }

            await axios.put(`/api/v1/reviews/${review.id}`, {
                manager_assessment: finalAssessment,
                status: 'manager_review_pending' // Actually it should probably be 'calibrated' or 'finished' depending on workflow
            });
            onSuccess();
        } catch (error) {
            console.error("Failed to submit assessment", error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen || !review || !employee) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-0">
            <div className="w-full max-w-md bg-[#0f121b] sm:rounded-3xl rounded-t-3xl border border-white/5 shadow-2xl animate-fade-up relative max-h-[90vh] flex flex-col overflow-hidden">

                {/* Header */}
                <div className="p-6 pb-0 flex items-center justify-between">
                    <button onClick={onClose} className="p-2 -ml-2 text-slate-400 hover:text-white transition-colors">
                        <X size={24} />
                    </button>
                    <h2 className="text-xl font-bold text-white">Manager Review</h2>
                    <div className="w-10"></div> {/* Spacer for centering */}
                </div>

                <p className="text-sm text-slate-400 text-center mt-2 mb-6 font-medium">
                    Reviewing {cycleName}
                </p>

                <div className="overflow-y-auto px-6 pb-24">
                    {/* Profile Card */}
                    <div className="bg-[#1a1d27] rounded-2xl p-4 flex items-center gap-4 border border-white/5 mb-8 shadow-lg">
                        <div className="relative">
                            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#b429f9] to-[#00e5ff] p-[2px]">
                                <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center">
                                    <UserIcon size={24} className="text-white" />
                                </div>
                            </div>
                            <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-emerald-400 border-2 border-[#1a1d27] rounded-full"></div>
                        </div>
                        <div>
                            <h3 className="font-bold text-lg text-white leading-tight">{employee.full_name}</h3>
                            <p className="text-sm text-slate-400 mb-1">{employee.job_title || 'Employee'}</p>
                            {employee.department && (
                                <span className="inline-block px-2.5 py-0.5 rounded-full bg-[#b429f9]/20 text-[#b429f9] text-[10px] font-bold uppercase tracking-wider">
                                    {employee.department} TEAM
                                </span>
                            )}
                        </div>
                    </div>

                    <form id="manager-assessment-form" onSubmit={handleSubmit} className="flex flex-col gap-8">

                        {/* Qualitative Feedback */}
                        <div>
                            <h4 className="text-xs font-bold text-slate-400 tracking-widest uppercase mb-3">Qualitative Feedback</h4>
                            <div className="relative">
                                <textarea
                                    value={assessmentText}
                                    onChange={(e) => setAssessmentText(e.target.value)}
                                    className="w-full bg-[#1a1d27] border border-white/5 rounded-2xl p-4 min-h-[160px] text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-[#00e5ff]/50 transition-colors resize-none"
                                    placeholder="Share detailed observations about performance, areas for growth, and specific achievements..."
                                    required
                                />
                                <div className="absolute bottom-4 right-4 text-xs text-slate-500 flex items-center gap-1">
                                    <span className="opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
                                </div>
                            </div>
                        </div>

                        {/* Key Strengths */}
                        <div>
                            <div className="flex items-center justify-between mb-3">
                                <h4 className="text-xs font-bold text-slate-400 tracking-widest uppercase">Key Strengths</h4>
                                <span className="text-xs text-[#b429f9] font-medium">Select up to 3</span>
                            </div>

                            <div className="flex flex-wrap gap-2.5">
                                {STRENGTHS.map(strength => {
                                    const isSelected = selectedStrengths.includes(strength.id);
                                    const Icon = strength.icon;
                                    return (
                                        <button
                                            key={strength.id}
                                            type="button"
                                            onClick={() => toggleStrength(strength.id)}
                                            className={`
                                                flex items-center gap-2 px-3.5 py-2 rounded-full text-sm font-medium transition-all duration-200 border
                                                ${isSelected
                                                    ? 'bg-[#b429f9]/15 border-[#b429f9] text-[#b429f9] shadow-[0_0_10px_rgba(180,41,249,0.2)]'
                                                    : 'bg-transparent border-white/10 text-slate-300 hover:border-white/20 hover:bg-white/5'
                                                }
                                            `}
                                        >
                                            <Icon size={14} className={isSelected ? 'text-[#b429f9]' : 'text-slate-400'} />
                                            {strength.label}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                    </form>
                </div>

                {/* Fixed Bottom Action Bar */}
                <div className="absolute bottom-0 left-0 right-0 p-6 pt-12 bg-gradient-to-t from-[#0f121b] via-[#0f121b] to-transparent">
                    <button
                        type="submit"
                        form="manager-assessment-form"
                        disabled={isLoading || !assessmentText}
                        className="w-full py-4 rounded-xl bg-gradient-to-r from-[#b429f9] to-[#00e5ff] text-white font-bold text-lg shadow-[0_10px_30px_rgba(180,41,249,0.3)] hover:shadow-[0_10px_40px_rgba(180,41,249,0.5)] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-1"
                    >
                        {isLoading ? <div className="loader"></div> : (
                            <>
                                Submit Feedback <Send size={18} className="ml-1" />
                            </>
                        )}
                    </button>
                </div>

            </div>
        </div>
    );
};
