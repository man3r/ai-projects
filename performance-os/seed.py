from app.database import SessionLocal
from app.models.tenant import Organization
from app.models.goal import GoalFramework, Goal
from app.models.user import User
from app.auth import get_password_hash

def seed():
    db = SessionLocal()
    
    # 1. Create the tenant
    print("Creating Organization...")
    org = Organization(name="Acme Corp", slug="acme")
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # 2. Create the User (Tenant Admin)
    print("Creating Tenant Admin User...")
    user = User(
        organization_id=org.id,
        email="admin@acme.com",
        full_name="Acme Admin",
        hashed_password=get_password_hash("password123"),
        role="Tenant Admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 3. Create the Food Safety Framework
    print("Creating Food Safety Framework...")
    fw = GoalFramework(
        organization_id=org.id,
        name="Food Safety PMS",
        tier1_name="Focus Area",
        tier2_name="Objective",
        tier3_name="Measure"
    )
    db.add(fw)
    db.commit()
    db.refresh(fw)
    
    # 4. Create the Goal Hierarchy
    print("Seeding Goals...")
    # Tier 1: Focus Area
    focus_area = Goal(
        organization_id=org.id,
        framework_id=fw.id,
        owner_id=user.id,
        title="Execution Excellence",
        tier_level=1
    )
    db.add(focus_area)
    db.commit()
    db.refresh(focus_area)
    
    # Tier 2: Objective
    objective = Goal(
        organization_id=org.id,
        framework_id=fw.id,
        parent_goal_id=focus_area.id,
        title="Gain Customer Trust",
        tier_level=2
    )
    db.add(objective)
    db.commit()
    db.refresh(objective)
    
    # Tier 3: Measure
    measure1 = Goal(
        organization_id=org.id,
        framework_id=fw.id,
        parent_goal_id=objective.id,
        title="Scope Compliance Rate: 100% adherence to SOW",
        tier_level=3,
        target_value=1.0, # 100%
        unit="percentage",
        weightage=0.20 # example 20% weight
    )
    
    measure2 = Goal(
        organization_id=org.id,
        framework_id=fw.id,
        parent_goal_id=objective.id,
        title="Escalation Lead Time (< 15 mins)",
        tier_level=3,
        target_value=15.0,
        unit="minutes",
        weightage=0.15 # 15% weight
    )
    
    db.add(measure1)
    db.add(measure2)
    db.commit()
    
    print("Seed Complete! Data is safely stored in the multi-tenant engine.")
    db.close()

if __name__ == "__main__":
    seed()
