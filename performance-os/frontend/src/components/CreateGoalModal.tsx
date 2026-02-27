import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save } from 'lucide-react';
import type { GoalFramework } from '../types/Goal';
interface CreateGoalModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const CreateGoalModal: React.FC<CreateGoalModalProps> = ({ isOpen, onClose, onSuccess }) => {
    // Removed unused user extraction
    const [frameworks, setFrameworks] = useState<GoalFramework[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        framework_id: '',
        tier_level: 1,
        target_value: '',
        unit: '',
        weightage: 100
    });

    useEffect(() => {
        if (isOpen) {
            fetchFrameworks();
        }
    }, [isOpen]);

    const fetchFrameworks = async () => {
        try {
            const response = await axios.get('/api/v1/goals/frameworks');
            setFrameworks(response.data);
            if (response.data.length > 0) {
                setFormData(prev => ({ ...prev, framework_id: response.data[0].id.toString() }));
            }
        } catch (error) {
            console.error("Failed to fetch frameworks", error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const payload = {
                title: formData.title,
                description: formData.description,
                framework_id: parseInt(formData.framework_id),
                tier_level: formData.tier_level,
                target_value: formData.target_value ? parseFloat(formData.target_value) : null,
                current_value: 0,
                unit: formData.unit || null,
                weightage: formData.weightage ? parseFloat(formData.weightage.toString()) : null,
                owner_id: null // Assuming backend sets this based on JWT or defaults to tenant
            };

            await axios.post('/api/v1/goals/', payload);
            setFormData({
                title: '',
                description: '',
                framework_id: frameworks.length > 0 ? frameworks[0].id.toString() : '',
                tier_level: 1,
                target_value: '',
                unit: '',
                weightage: 100
            });
            onSuccess();
        } catch (error) {
            console.error("Failed to create goal", error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    const selectedFramework = frameworks.find(f => f.id.toString() === formData.framework_id);

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
                    Create New Goal
                </h2>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Framework</label>
                        <select
                            name="framework_id"
                            value={formData.framework_id}
                            onChange={(e) => {
                                handleChange(e);
                                setFormData(prev => ({ ...prev, tier_level: 1 }));
                            }}
                            className="select w-full"
                            required
                        >
                            {frameworks.map(fw => (
                                <option key={fw.id} value={fw.id} className="bg-slate-800">{fw.name}</option>
                            ))}
                        </select>
                    </div>

                    {selectedFramework && (
                        <div className="flex gap-2 p-1 bg-[#1a1d27] rounded-pill border border-white/5">
                            <button
                                type="button"
                                onClick={() => setFormData(p => ({ ...p, tier_level: 1 }))}
                                className={`flex-1 py-2 text-sm font-medium rounded-pill transition-all ${formData.tier_level === 1 ? 'bg-[#b429f9] text-white' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                {selectedFramework.tier1_name}
                            </button>
                            <button
                                type="button"
                                onClick={() => setFormData(p => ({ ...p, tier_level: 2 }))}
                                className={`flex-1 py-2 text-sm font-medium rounded-pill transition-all ${formData.tier_level === 2 ? 'bg-[#00e5ff] text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                {selectedFramework.tier2_name}
                            </button>
                            <button
                                type="button"
                                onClick={() => setFormData(p => ({ ...p, tier_level: 3 }))}
                                className={`flex-1 py-2 text-sm font-medium rounded-pill transition-all ${formData.tier_level === 3 ? 'bg-emerald-400 text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                {selectedFramework.tier3_name}
                            </button>
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Title</label>
                        <input
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            className="input"
                            placeholder="e.g. Gain Customer Trust"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Description</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            className="textarea min-h-[100px] resize-none"
                            placeholder="Details about this objective..."
                        />
                    </div>

                    {(formData.tier_level === 2 || formData.tier_level === 3) && (
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Target</label>
                                <input
                                    type="number"
                                    name="target_value"
                                    value={formData.target_value}
                                    onChange={handleChange}
                                    className="input"
                                    placeholder="100"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Unit</label>
                                <input
                                    name="unit"
                                    value={formData.unit}
                                    onChange={handleChange}
                                    className="input"
                                    placeholder="%"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-slate-400 mb-1 ml-4">Weight %</label>
                                <input
                                    type="number"
                                    name="weightage"
                                    value={formData.weightage}
                                    onChange={handleChange}
                                    className="input"
                                    placeholder="25"
                                />
                            </div>
                        </div>
                    )}

                    <div className="mt-4 pt-4 border-t border-white/5 flex gap-4">
                        <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
                            Cancel
                        </button>
                        <button type="submit" disabled={isLoading} className="btn btn-primary flex-1">
                            {isLoading ? <div className="loader"></div> : <><Save size={18} /> Save Goal</>}
                        </button>
                    </div>

                </form>

            </div>
        </div>
    );
};
