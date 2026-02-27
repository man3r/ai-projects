export interface Feedback {
    id: number;
    organization_id: number;
    sender_id: number;
    receiver_id: number;
    feedback_type: string;
    message: string;
    is_public: boolean;
    created_at: string;
}

export interface UserResponse {
    id: number;
    email: string;
    full_name: string;
    job_title: string;
    department: string | null;
    role: string;
    organization_id: number;
    manager_id: number | null;
    is_active: boolean;
    created_at: string;
}
