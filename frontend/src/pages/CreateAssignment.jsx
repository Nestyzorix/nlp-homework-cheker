import { useState } from "react";

import api from "../utils/api";

import "./CreateAssignment.css";

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

    const createAssignment = async (event) => {

        event.preventDefault();

        const keywordList = keywords
            .split(",")
            .map((word) =>
                word.trim()
            )
            .filter(Boolean);

        await api.post(
            "/assignments",
            {
                question,
                reference_answer:
                    referenceAnswer,
                keywords:
                    keywordList
            }
        );

        alert("Задание создано");
        setQuestion("");
        setReferenceAnswer("");
        setKeywords("");
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

            <label>
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

            <label>
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
