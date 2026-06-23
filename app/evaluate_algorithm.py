from app.services.nlp_service import (
    apply_keyword_stuffing_penalty,
    apply_negation_penalty,
    final_score,
    generate_feedback,
    grade_from_score,
    keyword_score,
    semantic_similarity,
)


REFERENCE_ANSWER = (
    "SQL - это язык структурированных запросов, который используется "
    "для создания, изменения и получения данных из реляционных баз данных."
)

KEYWORDS = [
    "язык структурированных запросов",
    "реляционные базы данных",
    "получение данных",
]


TEST_CASES = [
    {
        "name": "Почти эталонный ответ",
        "answer": (
            "SQL - это язык структурированных запросов для создания, "
            "изменения и получения данных из реляционных баз данных."
        ),
        "expected": {5},
    },
    {
        "name": "Хороший перефразированный ответ",
        "answer": (
            "SQL применяют, чтобы работать с реляционными базами: "
            "выбирать, добавлять и менять хранящиеся данные."
        ),
        "expected": {4, 5},
    },
    {
        "name": "Частично верный ответ",
        "answer": (
            "SQL нужен для запросов к базам данных и помогает получать "
            "информацию из таблиц."
        ),
        "expected": {3, 4},
    },
    {
        "name": "Ключевые слова без нормального смысла",
        "answer": (
            "SQL реляционные базы данных получение данных язык "
            "структурированных запросов."
        ),
        "expected": {2, 3},
    },
    {
        "name": "Противоречие с отрицанием",
        "answer": (
            "SQL не используется для получения данных из реляционных баз "
            "данных."
        ),
        "expected": {2, 3},
    },
    {
        "name": "Неверная технология",
        "answer": (
            "HTML - это язык разметки, который нужен для создания структуры "
            "веб-страниц."
        ),
        "expected": {2},
    },
    {
        "name": "Пустой ответ",
        "answer": "",
        "expected": {2},
    },
    {
        "name": "Бессмысленный ответ",
        "answer": "Не знаю, какая-то штука для компьютеров.",
        "expected": {2},
    },
]


def evaluate_case(case):

    semantic = semantic_similarity(
        case["answer"],
        REFERENCE_ANSWER
    )

    keyword = keyword_score(
        case["answer"],
        KEYWORDS
    )

    score = final_score(
        semantic,
        keyword
    )

    score = apply_negation_penalty(
        score,
        REFERENCE_ANSWER,
        case["answer"]
    )

    score = apply_keyword_stuffing_penalty(
        score,
        case["answer"],
        KEYWORDS,
        REFERENCE_ANSWER
    )

    grade = grade_from_score(score)

    feedback = generate_feedback(
        case["answer"],
        KEYWORDS,
        score,
        REFERENCE_ANSWER
    )

    return {
        "semantic": semantic,
        "keyword": keyword,
        "score": score,
        "grade": grade,
        "passed": grade in case["expected"],
        "feedback": feedback,
    }


def main():

    passed = 0

    print("Диагностическая проверка алгоритма")
    print("=" * 42)

    for index, case in enumerate(TEST_CASES, start=1):

        result = evaluate_case(case)

        if result["passed"]:
            passed += 1

        status = "OK" if result["passed"] else "FAIL"
        expected = ", ".join(
            str(grade)
            for grade in sorted(case["expected"])
        )

        print(f"{index}. {case['name']} [{status}]")
        print(f"   expected: {expected}; actual: {result['grade']}")
        print(
            "   semantic: "
            f"{result['semantic']}; keyword: {result['keyword']}; "
            f"final: {result['score']}"
        )
        print(f"   feedback: {result['feedback']}")
        print()

    print(f"Итого: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    main()
