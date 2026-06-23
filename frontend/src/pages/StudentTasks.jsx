import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./StudentTasks.css";

const PROFILE_LABELS = {
    definition: "Определение понятия",
    process: "Описание процесса",
    factual: "Фактологическое объяснение",
    custom: "Пользовательская настройка"
};

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

                        <details className="student-result-details">
                            <summary>
                                Подробности проверки
                            </summary>

                            <div>
                                <span>
                                    Профиль:{" "}
                                    {
                                        PROFILE_LABELS[
                                            result.evaluation_profile
                                        ] || result.evaluation_profile
                                    }
                                </span>

                                <span>
                                    Семантическая близость:{" "}
                                    {result.semantic_score}
                                </span>

                                <span>
                                    Полнота ключевых элементов:{" "}
                                    {result.keyword_score}
                                </span>

                                <span>
                                    Скорректированный score:{" "}
                                    {result.corrected_score}
                                </span>

                                <span>
                                    Штрафы:{" "}
                                    {
                                        result.applied_penalties?.length
                                            ? result.applied_penalties
                                                .map((penalty) =>
                                                    penalty.reason
                                                )
                                                .join("; ")
                                            : "нет"
                                    }
                                </span>
                            </div>
                        </details>

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
