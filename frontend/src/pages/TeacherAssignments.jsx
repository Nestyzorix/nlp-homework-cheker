import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./TeacherAssignments.css";

const PROFILE_LABELS = {
    definition: "Определение понятия",
    process: "Описание процесса",
    factual: "Фактологическое объяснение",
    custom: "Пользовательская настройка"
};

function TeacherAssignments() {

    const [
        assignments,
        setAssignments
    ] = useState([]);

    async function fetchAssignments() {

        const response = await api.get(
            "/assignments"
        );

        setAssignments(response.data);
    }

    const deleteAssignment = async (assignmentId) => {

        await api.delete(
            `/assignments/${assignmentId}`
        );

        setAssignments((currentAssignments) =>
            currentAssignments.filter(
                (assignment) =>
                    assignment.id !== assignmentId
            )
        );
    };

    useEffect(() => {

        fetchAssignments();

    }, []);

    return (

        <div className="teacher-assignments">

            <h1>
                Созданные задания
            </h1>

            {
                assignments.length === 0 && (
                    <p className="teacher-assignments-empty">
                        Пока нет созданных заданий
                    </p>
                )
            }

            <div className="teacher-assignments-list">
                {
                    assignments.map((assignment) => (

                        <article
                            key={assignment.id}
                            className="teacher-assignment-card"
                        >
                            <p>
                                <b>Вопрос:</b> {assignment.question}
                            </p>

                            <p>
                                <b>Эталонный ответ:</b>{" "}
                                {assignment.reference_answer}
                            </p>

                            <p>
                                <b>Ключевые слова:</b>{" "}
                                {assignment.keywords || "Не указаны"}
                            </p>

                            <details className="teacher-assignment-details">
                                <summary>
                                    Параметры проверки
                                </summary>

                                <div className="teacher-assignment-config">
                                    <span>
                                        Профиль:{" "}
                                        {
                                            PROFILE_LABELS[
                                                assignment.evaluation_profile
                                            ] || assignment.evaluation_profile
                                        }
                                    </span>

                                    <span>
                                        Вес семантики:{" "}
                                        {assignment.semantic_weight}
                                    </span>

                                    <span>
                                        Вес ключевых слов:{" "}
                                        {assignment.keyword_weight}
                                    </span>

                                    <span>
                                        Пороги: 5 от{" "}
                                        {assignment.threshold_5}, 4 от{" "}
                                        {assignment.threshold_4}, 3 от{" "}
                                        {assignment.threshold_3}
                                    </span>

                                    <span>
                                        Штраф за отрицание:{" "}
                                        {
                                            assignment.negation_penalty_enabled
                                                ? "включен"
                                                : "отключен"
                                        }
                                    </span>

                                    <span>
                                        Штраф за перечисление ключевых слов:{" "}
                                        {
                                            assignment
                                                .keyword_stuffing_penalty_enabled
                                                ? "включен"
                                                : "отключен"
                                        }
                                    </span>
                                </div>
                            </details>

                            <button
                                type="button"
                                className="teacher-assignment-delete"
                                onClick={() =>
                                    deleteAssignment(assignment.id)
                                }
                            >
                                Удалить
                            </button>
                        </article>
                    ))
                }
            </div>

        </div>
    );
}

export default TeacherAssignments;
