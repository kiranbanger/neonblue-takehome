"""
Database models for the experimentation platform
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Experiment(Base):
    """Experiment model"""
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    client_id = Column(Integer, nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variants = relationship("Variant", back_populates="experiment", cascade="all, delete-orphan")
    assignments = relationship("UserAssignment", back_populates="experiment", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "client_id": self.client_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "variants": [v.to_dict() for v in self.variants]
        }


class Variant(Base):
    """Variant model"""
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False)
    name = Column(String(255), nullable=False)
    traffic_allocation = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="variants")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "traffic_allocation": self.traffic_allocation
        }


class UserAssignment(Base):
    """User assignment to variant"""
    __tablename__ = "user_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="assignments")

    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "variant_id": self.variant_id,
            "user_id": self.user_id,
            "assigned_at": self.assigned_at.isoformat()
        }


class Event(Base):
    """Event model"""
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    client_id = Column(Integer, nullable=False)
    event_type = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    properties = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "properties": self.properties
        }

