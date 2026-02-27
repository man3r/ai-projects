export interface GoalFramework {
    id: number;
    organization_id: number;
    name: string;
    tier1_name: string;
    tier2_name: string;
    tier3_name: string;
}

export interface Goal {
    id: number;
    organization_id: number;
    framework_id: number;
    parent_goal_id: number | null;
    owner_id: number | null;
    title: string;
    description: string | null;
    tier_level: number;
    target_value: number | null;
    current_value: number;
    unit: string | null;
    weightage: number | null;
    created_at: string;
}
