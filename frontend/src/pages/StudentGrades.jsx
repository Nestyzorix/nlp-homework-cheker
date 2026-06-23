import {
    useEffect,
    useState
} from "react";

import api from "../utils/api";

import "./StudentGrades.css";

const PROFILE_LABELS = {
    definition: "Определение понятия",
    process: "Описание процесса",
    factual: "Фактологическое объяснение",
    custom: "Пользовательская настройка"
};

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

                            <details className="student-grade-details">
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
                        </article>
                    ))
                }
            </div>

        </div>
    );
}

export default StudentGrades;
