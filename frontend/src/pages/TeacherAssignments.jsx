import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./TeacherAssignments.css";

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
