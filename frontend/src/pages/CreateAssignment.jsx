import { useMemo, useState } from "react";

import api from "../utils/api";

import "./CreateAssignment.css";

const PROFILE_OPTIONS = [
    {
        value: "definition",
        label: "Определение понятия"
    },
    {
        value: "process",
        label: "Описание процесса"
    },
    {
        value: "factual",
        label: "Фактологическое объяснение"
    },
    {
        value: "custom",
        label: "Пользовательская настройка"
    }
];

const STANDARD_CONFIGS = {
    definition: {
        semantic_weight: 0.7,
        keyword_weight: 0.3,
        threshold_5: 0.85,
        threshold_4: 0.7,
        threshold_3: 0.5,
        negation_penalty_enabled: true,
        keyword_stuffing_penalty_enabled: true
    },
    process: {
        semantic_weight: 0.6,
        keyword_weight: 0.4,
        threshold_5: 0.85,
        threshold_4: 0.7,
        threshold_3: 0.5,
        negation_penalty_enabled: true,
        keyword_stuffing_penalty_enabled: true
    },
    factual: {
        semantic_weight: 0.8,
        keyword_weight: 0.2,
        threshold_5: 0.85,
        threshold_4: 0.7,
        threshold_3: 0.5,
        negation_penalty_enabled: true,
        keyword_stuffing_penalty_enabled: true
    }
};

function CreateAssignment() {

    const [
        question,
        setQuestion
    ] = useState("");

    const [
        referenceAnswer,
        setReferenceAnswer
    ] = useState("");

    const [
        keywords,
        setKeywords
    ] = useState("");

    const [
        evaluationProfile,
        setEvaluationProfile
    ] = useState("factual");

    const [
        customConfig,
        setCustomConfig
    ] = useState({
        semantic_weight: "0.8",
        keyword_weight: "0.2",
        threshold_5: "0.85",
        threshold_4: "0.70",
        threshold_3: "0.50",
        negation_penalty_enabled: true,
        keyword_stuffing_penalty_enabled: true
    });

    const activeConfig = useMemo(() => {

        if (evaluationProfile === "custom") {

            return customConfig;
        }

        return STANDARD_CONFIGS[evaluationProfile];

    }, [
        customConfig,
        evaluationProfile
    ]);

    const updateCustomConfig = (field, value) => {

        setCustomConfig((currentConfig) => ({
            ...currentConfig,
            [field]: value
        }));
    };

    const createAssignment = async (event) => {

        event.preventDefault();

        const keywordList = keywords
            .split(",")
            .map((word) =>
                word.trim()
            )
            .filter(Boolean);

        const payload = {
            question,
            reference_answer:
                referenceAnswer,
            keywords:
                keywordList,
            evaluation_profile:
                evaluationProfile
        };

        if (evaluationProfile === "custom") {

            Object.assign(payload, {
                semantic_weight:
                    Number(customConfig.semantic_weight),
                keyword_weight:
                    Number(customConfig.keyword_weight),
                threshold_5:
                    Number(customConfig.threshold_5),
                threshold_4:
                    Number(customConfig.threshold_4),
                threshold_3:
                    Number(customConfig.threshold_3),
                negation_penalty_enabled:
                    customConfig.negation_penalty_enabled,
                keyword_stuffing_penalty_enabled:
                    customConfig.keyword_stuffing_penalty_enabled
            });
        }

        await api.post(
            "/assignments",
            payload
        );

        alert("Задание создано");
        setQuestion("");
        setReferenceAnswer("");
        setKeywords("");
        setEvaluationProfile("factual");
    };

    return (

        <form
            className="create-assignment"
            onSubmit={createAssignment}
        >

            <h1>
                Создание задания
            </h1>

            <label>
                <span>Тип проверяемого ответа</span>
                <select
                    value={evaluationProfile}
                    onChange={(event) =>
                        setEvaluationProfile(
                            event.target.value
                        )
                    }
                >
                    {
                        PROFILE_OPTIONS.map((option) => (

                            <option
                                key={option.value}
                                value={option.value}
                            >
                                {option.label}
                            </option>
                        ))
                    }
                </select>
            </label>

            <section className="create-assignment-config">
                <h2>
                    Параметры проверки
                </h2>

                <div className="create-assignment-config-grid">
                    <label>
                        <span>Вес семантики</span>
                        <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={activeConfig.semantic_weight}
                            readOnly={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "semantic_weight",
                                    event.target.value
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>Вес ключевых слов</span>
                        <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={activeConfig.keyword_weight}
                            readOnly={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "keyword_weight",
                                    event.target.value
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>Порог оценки 5</span>
                        <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={activeConfig.threshold_5}
                            readOnly={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "threshold_5",
                                    event.target.value
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>Порог оценки 4</span>
                        <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={activeConfig.threshold_4}
                            readOnly={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "threshold_4",
                                    event.target.value
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>Порог оценки 3</span>
                        <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={activeConfig.threshold_3}
                            readOnly={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "threshold_3",
                                    event.target.value
                                )
                            }
                        />
                    </label>
                </div>

                <div className="create-assignment-toggles">
                    <label>
                        <input
                            type="checkbox"
                            checked={activeConfig.negation_penalty_enabled}
                            disabled={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "negation_penalty_enabled",
                                    event.target.checked
                                )
                            }
                        />
                        <span>Штраф за вероятное смысловое отрицание</span>
                    </label>

                    <label>
                        <input
                            type="checkbox"
                            checked={
                                activeConfig.keyword_stuffing_penalty_enabled
                            }
                            disabled={evaluationProfile !== "custom"}
                            onChange={(event) =>
                                updateCustomConfig(
                                    "keyword_stuffing_penalty_enabled",
                                    event.target.checked
                                )
                            }
                        />
                        <span>Штраф за формальное перечисление ключевых слов</span>
                    </label>
                </div>
            </section>

            <label className="create-assignment-question">
                <span>Вопрос</span>
                <textarea
                    value={question}
                    onChange={(event) =>
                        setQuestion(
                            event.target.value
                        )
                    }
                    placeholder="Введите вопрос"
                    required
                />
            </label>

            <label className="create-assignment-reference">
                <span>Эталонный ответ</span>
                <textarea
                    value={referenceAnswer}
                    onChange={(event) =>
                        setReferenceAnswer(
                            event.target.value
                        )
                    }
                    placeholder="Введите эталонный ответ"
                    required
                />
            </label>

            <label className="create-assignment-keywords">
                <span>Ключевые слова</span>
                <textarea
                    value={keywords}
                    onChange={(event) =>
                        setKeywords(
                            event.target.value
                        )
                    }
                    placeholder="Введите ключевые слова через запятую"
                    required
                />
            </label>

            <button type="submit">
                Создать
            </button>

        </form>
    );
}

export default CreateAssignment;
