import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./TeacherAnswers.css";

function TeacherAnswers() {

    const [
        results,
        setResults
    ] = useState([]);

    async function fetchResults() {

        const response = await api.get(
            "/results"
        );

        setResults(response.data);
    }

    useEffect(() => {

        fetchResults();

    }, []);

    return (

        <div className="teacher-answers">

            <h1>
                Ответы студентов
            </h1>

            {
                results.length === 0 && (

                    <p className="teacher-answers-empty">
                        Пока нет ответов
                    </p>
                )
            }

            <div className="teacher-answers-list">
                {
                    results.map((result) => (

                        <article
                            key={result.id}
                            className="teacher-answer-card"
                        >
                            <div className="teacher-answer-header">
                                <span>
                                    {result.student_username}
                                </span>

                                <strong>
                                    Оценка: {result.grade}
                                </strong>
                            </div>

                            <p>
                                <b>Вопрос:</b> {result.question}
                            </p>

                            <p>
                                <b>Эталонный ответ:</b>{" "}
                                {result.reference_answer}
                            </p>

                            <p>
                                <b>Ключевые слова:</b>{" "}
                                {result.keywords || "Не указаны"}
                            </p>

                            <p>
                                <b>Ответ ученика:</b>{" "}
                                {result.student_answer}
                            </p>

                            <div className="teacher-answer-scores">
                                <span>
                                    Семантическая близость:{" "}
                                    {result.semantic_score}
                                </span>

                                <span>
                                    Ключевые слова:{" "}
                                    {result.keyword_score}
                                </span>

                                <span>
                                    Итоговый балл:{" "}
                                    {result.final_score}
                                </span>
                            </div>

                            <p>
                                <b>Отзыв:</b> {result.feedback}
                            </p>
                        </article>
                    ))
                }
            </div>

        </div>
    );
}

export default TeacherAnswers;
