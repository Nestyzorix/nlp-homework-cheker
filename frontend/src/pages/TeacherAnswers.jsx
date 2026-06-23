import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./TeacherAnswers.css";

const PROFILE_LABELS = {
    definition: "Определение понятия",
    process: "Описание процесса",
    factual: "Фактологическое объяснение",
    custom: "Пользовательская настройка"
};

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

                            <details className="teacher-answer-details">
                                <summary>
                                    Подробности проверки
                                </summary>

                                <div className="teacher-answer-details-grid">
                                    <span>
                                        Профиль:{" "}
                                        {
                                            PROFILE_LABELS[
                                                result.evaluation_profile
                                            ] || result.evaluation_profile
                                        }
                                    </span>

                                    <span>
                                        Исходный score:{" "}
                                        {result.raw_total_score}
                                    </span>

                                    <span>
                                        Скорректированный score:{" "}
                                        {result.corrected_score}
                                    </span>

                                    <span>
                                        Найденные ключевые элементы:{" "}
                                        {
                                            result.found_keywords?.length
                                                ? result.found_keywords.join(", ")
                                                : "нет"
                                        }
                                    </span>

                                    <span>
                                        Отсутствующие ключевые элементы:{" "}
                                        {
                                            result.missing_keywords?.length
                                                ? result.missing_keywords.join(", ")
                                                : "нет"
                                        }
                                    </span>

                                    <span>
                                        Примененные штрафы:{" "}
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
