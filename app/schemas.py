from pydantic import BaseModel


class CheckRequest(BaseModel):
    reference_answer: str
    student_answer: str
    keywords: list[str]

class AssignmentCreate(BaseModel):

    question: str
    reference_answer: str
    keywords: list[str]

class AssignmentResponse(BaseModel):

    id: int
    question: str
    reference_answer: str
    keywords: str
    is_visible: bool

    class Config:

        from_attributes = True


class SubmissionCreate(BaseModel):

    assignment_id: int
    student_answer: str


class ResultResponse(BaseModel):

    semantic_score: float
    keyword_score: float
    final_score: float
    grade: int
    feedback: str

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
    final_score: float
    grade: int
    feedback: str

    class Config:

        from_attributes = True

class UserRegister(BaseModel):

    username: str
    password: str
    role: str

class UserLogin(BaseModel):

    username: str
    password: str
