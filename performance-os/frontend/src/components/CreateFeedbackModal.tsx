import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Send } from 'lucide-react';
import type { UserResponse } from '../types/Feedback';

interface CreateFeedbackModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const CreateFeedbackModal: React.FC<CreateFeedbackModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const [users, setUsers] = useState<UserResponse[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        receiver_id: '',
        feedback_type: 'kudo',
        message: '',
        is_public: true
    });

    useEffect(() => {
        if (isOpen) {
            fetchUsers();
        }
    }, [isOpen]);

    const fetchUsers = async () => {
        try {
            const response = await axios.get('/api/v1/auth/users');
            setUsers(response.data);
            if (response.data.length > 0) {
                setFormData(prev => ({ ...prev, receiver_id: response.data[0].id.toString() }));
            }
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const payload = {
                receiver_id: parseInt(formData.receiver_id),
                feedback_type: formData.feedback_type,
                message: formData.message,
                is_public: formData.is_public
            };

            await axios.post('/api/v1/feedback/', payload);
            setFormData({
                receiver_id: users.length > 0 ? users[0].id.toString() : '',
                feedback_type: 'kudo',
                message: '',
                is_public: true
            });
            onSuccess();
        } catch (error) {
            console.error("Failed to submit feedback", error);
        } finally {
            setIsLoading(false);
        }
    };

    // Filter out the current user if possible, but we don't have user.id in context easily here without useAuth.
    // For now, listing all users in the tenant.

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-0">
            <div className="w-full max-w-lg glass-card animate-fade-up relative max-h-[90vh] overflow-y-auto">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-white/10"
                >
                    <X size={18} />
                </button>

                <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#00e5ff] to-[#b429f9] mb-6">
                    Give Feedback
                </h2>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Who is this for?</label>
                        <select
                            name="receiver_id"
                            value={formData.receiver_id}
                            onChange={handleChange}
                            className="select w-full"
                            required
                        >
                            {users.map(u => (
                                <option key={u.id} value={u.id} className="bg-slate-800">
                                    {u.full_name} ({u.job_title})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex gap-2 p-1 bg-[#1a1d27] rounded-pill border border-white/5">
                        <button
                            type="button"
                            onClick={() => setFormData(p => ({ ...p, feedback_type: 'kudo' }))}
                            className={`flex-1 py-2 text-sm font-medium rounded-pill transition-all ${formData.feedback_type === 'kudo' ? 'bg-emerald-400 text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
                        >
                            Give Kudos 🌟
                        </button>
                        <button
                            type="button"
                            onClick={() => setFormData(p => ({ ...p, feedback_type: 'constructive' }))}
                            className={`flex-1 py-2 text-sm font-medium rounded-pill transition-all ${formData.feedback_type === 'constructive' ? 'bg-[#b429f9] text-white' : 'text-slate-400 hover:text-slate-200'}`}
                        >
                            Constructive 📈
                        </button>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Message</label>
                        <textarea
                            name="message"
                            value={formData.message}
                            onChange={handleChange}
                            className="textarea min-h-[120px] resize-none"
                            placeholder="Share your thoughts..."
                            required
                        />
                    </div>

                    <div className="flex items-center ml-4 mt-2 mb-2">
                        <input
                            type="checkbox"
                            id="is_public"
                            name="is_public"
                            checked={formData.is_public}
                            onChange={handleChange}
                            className="w-4 h-4 rounded border-gray-600 outline-none accent-[#00e5ff] cursor-pointer"
                        />
                        <label htmlFor="is_public" className="ml-2 text-sm text-slate-400 cursor-pointer">
                            Make this feedback public in the timeline
                        </label>
                    </div>

                    <div className="mt-4 pt-4 border-t border-white/5 flex gap-4">
                        <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
                            Cancel
                        </button>
                        <button type="submit" disabled={isLoading || formData.receiver_id === ''} className="btn btn-primary flex-1">
                            {isLoading ? <div className="loader"></div> : <><Send size={18} /> Send Feedback</>}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    );
};
