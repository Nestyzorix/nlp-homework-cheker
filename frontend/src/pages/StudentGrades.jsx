import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./StudentGrades.css";

function StudentGrades() {

    const [
        results,
        setResults
    ] = useState([]);

    async function fetchResults() {

        const response = await api.get(
            "/my_results"
        );

        setResults(response.data);
    }

    useEffect(() => {

        fetchResults();

    }, []);

    return (

        <div className="student-grades">

            <h1>
                Мои оценки
            </h1>

            {
                results.length === 0 && (
                    <p className="student-grades-empty">
                        Пока нет проверенных ответов
                    </p>
                )
            }

            <div className="student-grades-list">
                {
                    results.map((result) => (

                        <article
                            key={result.id}
                            className="student-grade-card"
                        >
                            <div className="student-grade-header">
                                <span>
                                    Оценка: {result.grade}
                                </span>
                            </div>

                            <p>
                                <b>Вопрос:</b> {result.question}
                            </p>

                            <p>
                                <b>Ваш ответ:</b>{" "}
                                {result.student_answer}
                            </p>

                            <p>
                                <b>Обратная связь:</b>{" "}
                                {result.feedback}
                            </p>
                        </article>
                    ))
                }
            </div>

        </div>
    );
}

export default StudentGrades;
