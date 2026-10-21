"""Core data model for Fieldnote (SQLAlchemy, Postgres).

Schema changes go through Alembic: migrations/versions/.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Plan(enum.Enum):
    FREE = "free"
    TEAM = "team"
    BUSINESS = "business"


# Seats are counted as Membership rows in the workspace.
PLAN_SEAT_LIMITS = {
    Plan.FREE: 3,
    Plan.TEAM: 25,
    Plan.BUSINESS: None,  # unlimited
}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(320), nullable=False, unique=True)
    name = Column(String(200))
    password_hash = Column(String(200), nullable=False)
    email_verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    memberships = relationship("Membership", back_populates="user")

    def set_password(self, raw: str) -> None:
        from .auth import hash_password
        self.password_hash = hash_password(raw)


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    plan = Column(Enum(Plan), nullable=False, default=Plan.FREE)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    memberships = relationship("Membership", back_populates="workspace")

    def seats_used(self) -> int:
        return len(self.memberships)

    def seat_limit(self):
        return PLAN_SEAT_LIMITS[self.plan]


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "workspace_id"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="memberships")
    workspace = relationship("Workspace", back_populates="memberships")
