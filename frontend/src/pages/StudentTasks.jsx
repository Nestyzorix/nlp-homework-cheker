import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./StudentTasks.css";

function StudentTasks() {

    const [
        assignments,
        setAssignments
    ] = useState([]);

    const [
        selectedAssignment,
        setSelectedAssignment
    ] = useState(null);

    const [
        studentAnswer,
        setStudentAnswer
    ] = useState("");

    const [
        result,
        setResult
    ] = useState(null);

    async function fetchAssignments() {

        const response = await api.get(
            "/assignments"
        );

        setAssignments(
            response.data
        );
    }

    useEffect(() => {

        fetchAssignments();

    }, []);

    const openAssignment = (assignment) => {

        setSelectedAssignment(assignment);
        setStudentAnswer("");
    };

    const closeAssignment = () => {

        setSelectedAssignment(null);
        setStudentAnswer("");
    };

    const submitAnswer = async (event) => {

        event.preventDefault();

        const response = await api.post(
            "/submit_answer",
            {
                assignment_id:
                    selectedAssignment.id,

                student_answer:
                    studentAnswer
            }
        );

        setResult(response.data);
        closeAssignment();
    };

    return (

        <div className="student-tasks">

            <h1>
                Задания
            </h1>

            <div className="student-tasks-list">

                {
                    assignments.length === 0 && (
                        <p className="student-tasks-empty">
                            Пока нет доступных заданий
                        </p>
                    )
                }

                {
                    assignments.map(
                        (assignment) => (

                            <button
                                type="button"
                                key={assignment.id}
                                className="student-task-card"
                                onClick={() =>
                                    openAssignment(assignment)
                                }
                            >
                                <span>
                                    {assignment.question}
                                </span>
                            </button>
                        )
                    )
                }

            </div>

            {
                result && (

                    <section className="student-result">

                        <h2>
                            Результат
                        </h2>

                        <p>
                            Оценка: {result.grade}
                        </p>

                        <p>
                            Отзыв: {result.feedback}
                        </p>

                    </section>
                )
            }

            {
                selectedAssignment && (

                    <div
                        className="student-task-modal-backdrop"
                        role="presentation"
                    >
                        <form
                            className="student-task-modal"
                            onSubmit={submitAnswer}
                            role="dialog"
                            aria-modal="true"
                            aria-labelledby="student-task-modal-title"
                        >
                            <button
                                type="button"
                                className="student-task-modal-close"
                                onClick={closeAssignment}
                                aria-label="Закрыть"
                            >
                                ×
                            </button>

                            <h2 id="student-task-modal-title">
                                Вопрос
                            </h2>

                            <p className="student-task-modal-question">
                                {selectedAssignment.question}
                            </p>

                            <textarea
                                value={studentAnswer}
                                onChange={(event) =>
                                    setStudentAnswer(
                                        event.target.value
                                    )
                                }
                                placeholder="Введите ответ"
                                required
                            />

                            <button
                                type="submit"
                                className="student-task-submit"
                            >
                                Отправить ответ
                            </button>
                        </form>
                    </div>
                )
            }

        </div>
    );
}

export default StudentTasks;
