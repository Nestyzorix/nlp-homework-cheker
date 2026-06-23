from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import text

from app.database import (
    engine,
    get_db
)

from app.models import (
    Base,
    User,
    Assignment,
    Submission,
    Result
)

from app.schemas import (
    CheckRequest,

    AssignmentCreate,
    AssignmentResponse,

    SubmissionCreate,
    SubmissionResponse,

    ResultResponse,
    ResultDetailResponse,

    UserRegister,
    UserLogin
)

from app.services.nlp_service import (
    semantic_similarity,
    keyword_score,
    final_score,
    generate_feedback,
    grade_from_score,
    apply_negation_penalty,
    apply_keyword_stuffing_penalty
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_role
)


app = FastAPI()


app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


Base.metadata.create_all(
    bind=engine
)


def ensure_database_columns():

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                ALTER TABLE submissions
                ADD COLUMN IF NOT EXISTS student_id
                INTEGER REFERENCES users(id)
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE assignments
                ADD COLUMN IF NOT EXISTS teacher_id
                INTEGER REFERENCES users(id)
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE assignments
                ADD COLUMN IF NOT EXISTS is_visible
                BOOLEAN DEFAULT TRUE NOT NULL
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE assignments
                SET is_visible = TRUE
                WHERE is_visible IS NULL
                """
            )
        )


ensure_database_columns()


@app.get("/")
def root():

    return {
        "message":
        "NLP Homework Checker API"
    }


# =========================
# AUTH
# =========================

@app.post("/register")
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):

    existing_user = db.query(
        User
    ).filter(
        User.username == data.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    if data.role not in {
        "student",
        "teacher"
    }:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    hashed_password = hash_password(
        data.password
    )

    user = User(

        username=data.username,

        password=hashed_password,

        role=data.role
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message":
        "User created"
    }


@app.post("/login")
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    valid_password = verify_password(
        data.password,
        user.password
    )

    if not valid_password:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({

        "sub": user.username,

        "role": user.role,

        "user_id": user.id
    })

    return {

        "access_token": token,

        "role": user.role
    }


# =========================
# NLP CHECK
# =========================

@app.post("/check")
def check_answer(data: CheckRequest):

    semantic = semantic_similarity(
        data.student_answer,
        data.reference_answer
    )

    keyword = keyword_score(
        data.student_answer,
        data.keywords
    )

    final = final_score(
        semantic,
        keyword
    )

    final = apply_negation_penalty(
        final,
        data.reference_answer,
        data.student_answer
    )

    final = apply_keyword_stuffing_penalty(
        final,
        data.student_answer,
        data.keywords,
        data.reference_answer
    )

    grade = grade_from_score(final)

    feedback = generate_feedback(
        data.student_answer,
        data.keywords,
        final,
        data.reference_answer
    )

    return {

        "semantic_score":
            semantic,

        "keyword_score":
            keyword,

        "final_score":
            final,

        "grade":
            grade,

        "feedback":
            feedback
    }


# =========================
# ASSIGNMENTS
# =========================

@app.post(
    "/assignments",
    response_model=AssignmentResponse
)
def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("teacher")
    )
):

    assignment = Assignment(

        question=data.question,

        reference_answer=
            data.reference_answer,

        keywords=
            ", ".join(data.keywords),

        teacher_id=current_user.id,

        is_visible=True
    )

    db.add(assignment)

    db.commit()

    db.refresh(assignment)

    return assignment


@app.get(
    "/assignments",
    response_model=list[AssignmentResponse]
)
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(
        Assignment
    ).filter(
        Assignment.is_visible == True
    )

    if current_user.role == "teacher":

        query = query.filter(
            Assignment.teacher_id == current_user.id
        )

    assignments = query.all()

    return assignments


@app.get(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    assignment = db.query(
        Assignment
    ).filter(
        Assignment.id == assignment_id,
        Assignment.is_visible == True
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    return assignment


@app.delete("/assignments/{assignment_id}")
def hide_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("teacher")
    )
):

    assignment = db.query(
        Assignment
    ).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id,
        Assignment.is_visible == True
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    assignment.is_visible = False

    db.commit()

    return {
        "message": "Assignment hidden"
    }


# =========================
# SUBMISSIONS
# =========================

@app.post(
    "/submit_answer",
    response_model=ResultResponse
)
def submit_answer(
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("student")
    )
):

    assignment = db.query(
        Assignment
    ).filter(
        Assignment.id == data.assignment_id,
        Assignment.is_visible == True
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    submission = Submission(

        assignment_id=
            data.assignment_id,

        student_answer=
            data.student_answer,

        student_id=current_user.id
    )

    db.add(submission)

    db.commit()

    db.refresh(submission)

    keywords = assignment.keywords.split(", ")

    semantic = semantic_similarity(
        data.student_answer,
        assignment.reference_answer
    )

    keyword = keyword_score(
        data.student_answer,
        keywords
    )

    final = final_score(
        semantic,
        keyword
    )

    final = apply_negation_penalty(
        final,
        assignment.reference_answer,
        data.student_answer
    )

    final = apply_keyword_stuffing_penalty(
        final,
        data.student_answer,
        keywords,
        assignment.reference_answer
    )

    grade = grade_from_score(final)

    feedback = generate_feedback(
        data.student_answer,
        keywords,
        final,
        assignment.reference_answer
    )

    result = Result(

        submission_id=submission.id,

        semantic_score=semantic,

        keyword_score=keyword,

        final_score=final,

        grade=grade,

        feedback=feedback
    )

    db.add(result)

    db.commit()

    db.refresh(result)

    return result


@app.get(
    "/assignments/{assignment_id}/submissions",
    response_model=list[SubmissionResponse]
)
def get_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("teacher")
    )
):

    submissions = db.query(
        Submission
    ).filter(
        Submission.assignment_id == assignment_id
    ).all()

    return submissions


# =========================
# RESULTS
# =========================

def result_to_detail(result: Result):

    submission = result.submission
    assignment = submission.assignment if submission else None
    student = submission.student if submission else None

    return {
        "id": result.id,
        "submission_id": result.submission_id,
        "question": (
            assignment.question
            if assignment
            else "Вопрос не найден"
        ),
        "reference_answer": (
            assignment.reference_answer
            if assignment
            else "Эталонный ответ не найден"
        ),
        "keywords": (
            assignment.keywords
            if assignment
            else ""
        ),
        "student_answer": (
            submission.student_answer
            if submission
            else "Ответ не найден"
        ),
        "student_username": (
            student.username
            if student
            else "Неизвестный пользователь"
        ),
        "semantic_score": result.semantic_score,
        "keyword_score": result.keyword_score,
        "final_score": result.final_score,
        "grade": result.grade,
        "feedback": result.feedback
    }


@app.get(
    "/results",
    response_model=list[ResultDetailResponse]
)
def get_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("teacher")
    )
):

    results = db.query(
        Result
    ).options(
        joinedload(Result.submission)
        .joinedload(Submission.assignment),
        joinedload(Result.submission)
        .joinedload(Submission.student)
    ).all()

    return [
        result_to_detail(result)
        for result in results
    ]


@app.get(
    "/my_results",
    response_model=list[ResultDetailResponse]
)
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("student")
    )
):

    results = db.query(
        Result
    ).join(
        Submission
    ).options(
        joinedload(Result.submission)
        .joinedload(Submission.assignment),
        joinedload(Result.submission)
        .joinedload(Submission.student)
    ).filter(
        Submission.student_id == current_user.id
    ).all()

    return [
        result_to_detail(result)
        for result in results
    ]


@app.get(
    "/results/{result_id}",
    response_model=ResultDetailResponse
)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("teacher")
    )
):

    result = db.query(
        Result
    ).options(
        joinedload(Result.submission)
        .joinedload(Submission.assignment),
        joinedload(Result.submission)
        .joinedload(Submission.student)
    ).filter(
        Result.id == result_id
    ).first()

    if not result:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )

    return result_to_detail(result)
