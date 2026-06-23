from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    assignments = relationship(
        "Assignment",
        back_populates="teacher"
    )

    submissions = relationship(
        "Submission",
        back_populates="student"
    )


class Assignment(Base):

    __tablename__ = "assignments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    question = Column(
        String,
        nullable=False
    )

    reference_answer = Column(
        Text,
        nullable=False
    )

    keywords = Column(
        Text,
        nullable=False
    )

    teacher_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    is_visible = Column(
        Boolean,
        default=True,
        nullable=False
    )

    evaluation_profile = Column(
        String,
        default="factual",
        nullable=False
    )

    semantic_weight = Column(
        Float
    )

    keyword_weight = Column(
        Float
    )

    threshold_5 = Column(
        Float
    )

    threshold_4 = Column(
        Float
    )

    threshold_3 = Column(
        Float
    )

    negation_penalty_enabled = Column(
        Boolean,
        default=True
    )

    keyword_stuffing_penalty_enabled = Column(
        Boolean,
        default=True
    )

    teacher = relationship(
        "User",
        back_populates="assignments"
    )


class Submission(Base):

    __tablename__ = "submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id")
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    student_answer = Column(
        Text,
        nullable=False
    )

    submitted_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    assignment = relationship(
        "Assignment"
    )

    student = relationship(
        "User",
        back_populates="submissions"
    )


class Result(Base):

    __tablename__ = "results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    submission_id = Column(
        Integer,
        ForeignKey("submissions.id")
    )

    semantic_score = Column(
        Float
    )

    keyword_score = Column(
        Float
    )

    final_score = Column(
        Float
    )

    raw_total_score = Column(
        Float
    )

    corrected_score = Column(
        Float
    )

    grade = Column(
        Integer
    )

    feedback = Column(
        Text
    )

    found_keywords = Column(
        Text
    )

    missing_keywords = Column(
        Text
    )

    applied_penalties = Column(
        Text
    )

    evaluation_profile = Column(
        String
    )

    evaluation_config = Column(
        Text
    )

    checked_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    submission = relationship(
        "Submission"
    )
