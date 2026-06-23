from typing import Any

from pydantic import BaseModel
from pydantic import Field


class EvaluationConfigRequest(BaseModel):

    semantic_weight: float | None = None
    keyword_weight: float | None = None
    threshold_5: float | None = None
    threshold_4: float | None = None
    threshold_3: float | None = None
    negation_penalty_enabled: bool | None = None
    negation_penalty_value: float | None = None
    keyword_stuffing_penalty_enabled: bool | None = None
    keyword_stuffing_penalty_value: float | None = None


class CheckRequest(BaseModel):

    question: str | None = None
    reference_answer: str
    student_answer: str
    keywords: list[str]
    evaluation_profile: str = "factual"
    custom_config: EvaluationConfigRequest | None = None

class AssignmentCreate(BaseModel):

    question: str
    reference_answer: str
    keywords: list[str]
    evaluation_profile: str = "factual"
    semantic_weight: float | None = None
    keyword_weight: float | None = None
    threshold_5: float | None = None
    threshold_4: float | None = None
    threshold_3: float | None = None
    negation_penalty_enabled: bool | None = None
    keyword_stuffing_penalty_enabled: bool | None = None

class AssignmentResponse(BaseModel):

    id: int
    question: str
    reference_answer: str
    keywords: str
    is_visible: bool
    evaluation_profile: str = "factual"
    semantic_weight: float | None = None
    keyword_weight: float | None = None
    threshold_5: float | None = None
    threshold_4: float | None = None
    threshold_3: float | None = None
    negation_penalty_enabled: bool | None = None
    keyword_stuffing_penalty_enabled: bool | None = None

    class Config:

        from_attributes = True


class SubmissionCreate(BaseModel):

    assignment_id: int
    student_answer: str


class ResultResponse(BaseModel):

    semantic_score: float
    keyword_score: float
    raw_total_score: float | None = None
    corrected_score: float | None = None
    final_score: float
    grade: int
    feedback: str
    found_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    applied_penalties: list[dict[str, Any]] = Field(default_factory=list)
    evaluation_profile: str = "factual"
    evaluation_config: dict[str, Any] | None = None

    class Config:

        from_attributes = True


class SubmissionResponse(BaseModel):

    id: int
    assignment_id: int
    student_answer: str

    class Config:

        from_attributes = True


class ResultDetailResponse(BaseModel):

    id: int
    submission_id: int
    question: str
    reference_answer: str
    keywords: str
    student_answer: str
    student_username: str
    semantic_score: float
    keyword_score: float
    raw_total_score: float | None = None
    corrected_score: float | None = None
    final_score: float
    grade: int
    feedback: str
    found_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    applied_penalties: list[dict[str, Any]] = Field(default_factory=list)
    evaluation_profile: str = "factual"
    evaluation_config: dict[str, Any] | None = None

    class Config:

        from_attributes = True

class UserRegister(BaseModel):

    username: str
    password: str
    role: str

class UserLogin(BaseModel):

    username: str
    password: str
