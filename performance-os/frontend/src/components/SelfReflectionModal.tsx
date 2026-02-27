import React, { useState } from 'react';
import axios from 'axios';
import { X, Save } from 'lucide-react';
import type { Review } from '../types/Review';

interface SelfReflectionModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    review: Review | null;
    cycleName: string;
}

export const SelfReflectionModal: React.FC<SelfReflectionModalProps> = ({ isOpen, onClose, onSuccess, review, cycleName }) => {
    const [reflectionText, setReflectionText] = useState(review?.self_reflection || '');
    const [isLoading, setIsLoading] = useState(false);

    // Update internal state when a new review object is passed in
    React.useEffect(() => {
        if (review) {
            setReflectionText(review.self_reflection || '');
        }
    }, [review]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!review) return;

        setIsLoading(true);

        try {
            await axios.put(`/api/v1/reviews/${review.id}`, {
                self_reflection: reflectionText,
                status: 'manager_review_pending' // Progress the status
            });
            onSuccess();
        } catch (error) {
            console.error("Failed to submit reflection", error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen || !review) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-0">
            <div className="w-full max-w-2xl glass-card animate-fade-up relative max-h-[90vh] flex flex-col">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-white/10"
                >
                    <X size={18} />
                </button>

                <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#00e5ff] to-[#b429f9] mb-1">
                    Self Reflection
                </h2>
                <p className="text-sm text-slate-400 mb-6 font-medium">{cycleName}</p>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4 flex-1 overflow-y-auto">

                    <div className="bg-slate-800/50 p-4 rounded-xl border border-white/5 mb-2 text-sm text-slate-300 leading-relaxed">
                        <h4 className="font-semibold text-slate-200 mb-2">Instructions</h4>
                        Reflect on your achievements and areas of growth since the last review cycle.
                        Consider how you've demonstrated the company values (e.g. Integrity, Transparency) and progressed on your specific Objectives.
                    </div>

                    <div className="flex-1 flex flex-col">
                        <label className="block text-sm font-medium text-[#00e5ff] mb-2 ml-4">Your Reflection</label>
                        <textarea
                            name="self_reflection"
                            value={reflectionText}
                            onChange={(e) => setReflectionText(e.target.value)}
                            className="textarea min-h-[250px] resize-none flex-1 font-sans text-base leading-relaxed"
                            placeholder="I am particularly proud of my work on..."
                            required
                        />
                    </div>

                    <div className="mt-4 pt-4 border-t border-white/5 flex gap-4 shrink-0">
                        <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
                            Cancel
                        </button>
                        <button type="submit" disabled={isLoading || !reflectionText} className="btn btn-primary flex-1">
                            {isLoading ? <div className="loader"></div> : <><Save size={18} /> Submit Assessment</>}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    );
};
