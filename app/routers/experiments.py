"""
Experiments router for the experimentation platform
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
import hashlib
import pandas as pd

from app.models import Experiment, Variant, UserAssignment, Event
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

    return experiment.to_dict() # TODO don't return client_id or variant_id


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
            "created_at": existing_assignment.created_at.isoformat(),
            "updated_at": existing_assignment.updated_at.isoformat()
        }

    # Assign user to variant based on traffic allocation
    # Use deterministic hashing for idempotency
    hash_input = f"{experiment_id}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    random_value = (hash_value % 100) + 1

    cumulative = 0
    selected_variant = None
    variants = experiment.variants
    variants.sort(key=lambda x: x.id)
    for variant in variants:
        cumulative += variant.traffic_allocation
        if random_value <= cumulative:
            selected_variant = variant
            break

    if not selected_variant:
        selected_variant = variants[-1]

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
        "created_at": assignment.created_at.isoformat(),
        "updated_at": assignment.updated_at.isoformat()
    }


@router.get("/{experiment_id}/results")
async def get_results(
    experiment_id: str,
    client_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get experiment performance summary"""

    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.client_id == client_id).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

    event_data = db.query(
        UserAssignment.user_id,
        Variant.name,
        Event.id,
        Event.event_type,
        Event.properties
    ).join(
        Event, Event.user_id == UserAssignment.user_id
    ).join(
        Variant, Variant.id == UserAssignment.variant_id
    ).filter(
        UserAssignment.experiment_id == experiment_id,
        Event.timestamp > UserAssignment.created_at
    ).all()

    df = pd.DataFrame([
        {
            "user_id": row.user_id,
            "variant_name": row.name,
            "event_id": row.id,
            "event_type": row.event_type,
            "properties": row.properties
        }
        for row in event_data
    ])
    
    df.drop_duplicates(subset=["event_id"], inplace=True)
    user_count_by_variant_df = df.groupby('variant_name')['user_id'].nunique().reset_index()
    user_count_by_variant_df.rename(columns={"user_id": "user_count"}, inplace=True)
    user_count_by_variant_type_df = df.groupby(['variant_name', 'event_type'])['user_id'].nunique().reset_index()
    user_count_by_variant_type_df.rename(columns={"user_id": "user_count_event_type"}, inplace=True)

    agg_data = pd.merge(user_count_by_variant_df, user_count_by_variant_type_df, on='variant_name', how='left')
    agg_data['conversion_rate'] = agg_data['user_count_event_type'] / agg_data['user_count']

    return agg_data.to_dict("records")
