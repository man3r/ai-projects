export interface ReviewCycle {
    id: number;
    organization_id: number;
    name: string;
    start_date: string;
    end_date: string;
    status: string;
    created_at: string;
}

export interface Review {
    id: number;
    organization_id: number;
    cycle_id: number;
    employee_id: number;
    manager_id: number | null;
    self_reflection: string | null;
    manager_assessment: string | null;
    final_rating: number | null;
    status: string;
    created_at: string;
    updated_at: string | null;
}
