from app.database import SessionLocal
from app.models.review import ReviewCycle, Review
from datetime import datetime, timedelta

def seed():
    db = SessionLocal()
    
    # Check if a cycle exists
    cycle = db.query(ReviewCycle).first()
    if not cycle:
        cycle = ReviewCycle(
            organization_id=1,
            name="Q4 Performance Cycle",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            status="active"
        )
        db.add(cycle)
        db.commit()
        db.refresh(cycle)
        print(f"Created cycle: {cycle.id}")
    else:
        print(f"Cycle already exists: {cycle.id}")
        
    # Check if a review exists for employee_id=1
    review = db.query(Review).filter(Review.employee_id == 1).first()
    if not review:
        review = Review(
            organization_id=1,
            cycle_id=cycle.id,
            employee_id=1, # Admin user
            manager_id=1,  # Self-managed for now to test UI
            status="self_reflection_pending"
        )
        db.add(review)
        db.commit()
        print(f"Created review: {review.id}")
    else:
        print(f"Review already exists: {review.id}")
        
    db.close()

if __name__ == "__main__":
    seed()
