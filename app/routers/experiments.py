"""
Experiments router for the experimentation platform
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
import hashlib

from app.models import Experiment, Variant, UserAssignment
from app.auth import verify_token
from app.database import get_db

router = APIRouter(prefix="/experiments", tags=["experiments"])


class VariantInput(BaseModel):
    """Variant input model"""
    name: str
    traffic_allocation: float


class ExperimentInput(BaseModel):
    """Experiment input model"""
    name: str
    description: Optional[str] = None
    variants: List[VariantInput]


@router.post("/", status_code=201)
async def create_experiment(
    data: ExperimentInput,
    client_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new experiment with variants"""
    
    # Validate traffic allocation sums to 100
    total_allocation = sum(v.traffic_allocation for v in data.variants)
    if total_allocation != 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Traffic allocation must sum to 100, got {total_allocation}"
        )

    # Create experiment
    experiment = Experiment(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        client_id=client_id,
        status="active"
    )

    # Create variants
    for variant_data in data.variants:
        variant = Variant(
            experiment_id=experiment.id,
            name=variant_data.name,
            traffic_allocation=variant_data.traffic_allocation
        )
        experiment.variants.append(variant)

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return experiment.to_dict()


@router.get("/{experiment_id}/assignment/{user_id}")
async def get_assignment(
    experiment_id: str,
    user_id: str,
    client_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user's variant assignment (idempotent)"""
    
    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.client_id == client_id).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

    # Check if user already has assignment
    existing_assignment = db.query(UserAssignment).filter(
        UserAssignment.experiment_id == experiment_id,
        UserAssignment.user_id == user_id
    ).first()

    if existing_assignment:
        variant = db.query(Variant).filter(Variant.id == existing_assignment.variant_id).first()
        return {
            "id": existing_assignment.id,
            "experiment_id": existing_assignment.experiment_id,
            "variant_id": existing_assignment.variant_id,
            "variant_name": variant.name,
            "user_id": existing_assignment.user_id,
            "assigned_at": existing_assignment.assigned_at.isoformat()
        }

    # Assign user to variant based on traffic allocation
    # Use deterministic hashing for idempotency
    hash_input = f"{experiment_id}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    random_value = (hash_value % 100) + 1

    cumulative = 0
    selected_variant = None
    for variant in experiment.variants:
        cumulative += variant.traffic_allocation
        if random_value <= cumulative:
            selected_variant = variant
            break

    if not selected_variant:
        selected_variant = experiment.variants[-1]

    # Create assignment
    assignment = UserAssignment(
        id=str(uuid.uuid4()),
        experiment_id=experiment_id,
        variant_id=selected_variant.id,
        user_id=user_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "id": assignment.id,
        "experiment_id": assignment.experiment_id,
        "variant_id": assignment.variant_id,
        "variant_name": selected_variant.name,
        "user_id": assignment.user_id,
        "assigned_at": assignment.assigned_at.isoformat()
    }


@router.get("/{experiment_id}/results")
async def get_results(
    experiment_id: str,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    client_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get experiment performance summary"""
    from app.models import Event
    from datetime import datetime

    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.client_id == client_id).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

    # Get all assignments for this experiment
    assignments = db.query(UserAssignment).filter(
        UserAssignment.experiment_id == experiment_id
    ).all()

    # Build results by variant
    results = {
        "experiment_id": experiment_id,
        "experiment_name": experiment.name,
        "total_users": len(set(a.user_id for a in assignments)),
        "variants": {}
    }

    for variant in experiment.variants:
        variant_assignments = [a for a in assignments if a.variant_id == variant.id]
        variant_users = set(a.user_id for a in variant_assignments)

        # Get events for users in this variant after their assignment
        events_query = db.query(Event)
        
        if event_type:
            events_query = events_query.filter(Event.event_type == event_type)

        variant_events = []
        for assignment in variant_assignments:
            user_events = events_query.filter(
                Event.user_id == assignment.user_id,
                Event.timestamp >= assignment.assigned_at
            ).all()
            variant_events.extend(user_events)

        # Count events by type
        events_by_type = {}
        for event in variant_events:
            events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1

        # Calculate conversion rate (users with at least one event)
        users_with_events = set(e.user_id for e in variant_events)
        conversion_rate = len(users_with_events) / len(variant_users) if variant_users else 0

        results["variants"][variant.name] = {
            "variant_id": variant.id,
            "traffic_allocation": variant.traffic_allocation,
            "user_count": len(variant_users),
            "event_count": len(variant_events),
            "events_by_type": events_by_type,
            "conversion_rate": conversion_rate
        }

    # Add summary
    total_events = sum(v["event_count"] for v in results["variants"].values())
    avg_events = total_events / results["total_users"] if results["total_users"] > 0 else 0

    results["summary"] = {
        "total_events": total_events,
        "average_events_per_user": avg_events
    }

    return results

