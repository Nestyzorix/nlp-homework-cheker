from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.preprocessing import preprocess_text

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def semantic_similarity(answer, reference):

    embeddings = model.encode([
        answer,
        reference
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(float(similarity), 2)


def keyword_score(answer, keywords):

    processed_answer = set(
        preprocess_text(answer)
    )

    keyword_coverages = []

    for keyword in keywords:

        processed_keyword = preprocess_text(keyword)

        if not processed_keyword:
            continue

        matched_words = sum(
            1
            for word in processed_keyword
            if word in processed_answer
        )

        keyword_coverages.append(
            matched_words / len(processed_keyword)
        )

    if len(keyword_coverages) == 0:
        return 0

    score = sum(keyword_coverages) / len(keyword_coverages)

    return round(score, 2)


def final_score(
    semantic_score,
    keyword_score_value
):

    result = (
        0.8 * semantic_score +
        0.2 * keyword_score_value
    )

    return round(result, 2)


def get_keyword_lemmas(keywords):

    keyword_lemmas = set()

    for keyword in keywords:

        keyword_lemmas.update(
            preprocess_text(keyword)
        )

    return keyword_lemmas


def has_explanation_marker(answer):

    normalized_answer = f" {answer.lower()} "

    markers = [
        " это ",
        " является ",
        " используют ",
        " используется ",
        " нужен ",
        " нужна ",
        " нужно ",
        " для ",
        " чтобы ",
        " который ",
        " которая ",
        " которое ",
        " позволяет ",
        " помогает ",
        " служит ",
        " - ",
        " — ",
    ]

    return any(
        marker in normalized_answer
        for marker in markers
    )


def is_keyword_stuffing(
    answer,
    keywords,
    reference_answer=None
):

    answer_lemmas = preprocess_text(answer)

    if len(answer_lemmas) < 5:
        return False

    keyword_lemmas = get_keyword_lemmas(keywords)

    if not keyword_lemmas:
        return False

    keyword_word_count = sum(
        1
        for lemma in answer_lemmas
        if lemma in keyword_lemmas
    )

    non_keyword_word_count = len(answer_lemmas) - keyword_word_count

    keyword_density = keyword_word_count / len(answer_lemmas)

    if has_explanation_marker(answer):
        return False

    if reference_answer:

        reference_lemmas = preprocess_text(reference_answer)

        if len(reference_lemmas) <= 8:
            return False

        answer_is_much_shorter = (
            len(answer_lemmas)
            <= len(reference_lemmas) * 0.75
        )

    else:

        answer_is_much_shorter = True

    return (
        keyword_density >= 0.75
        and non_keyword_word_count <= 2
        and answer_is_much_shorter
    )


def apply_keyword_stuffing_penalty(
    score,
    answer,
    keywords,
    reference_answer=None
):

    if is_keyword_stuffing(
        answer,
        keywords,
        reference_answer
    ):

        return min(
            score,
            0.59
        )

    return score


def generate_feedback(
    answer,
    keywords,
    final_score,
    reference_answer=None
):

    processed_answer = preprocess_text(answer)

    missing_keywords = []

    for keyword in keywords:

        processed_keyword = preprocess_text(keyword)

        if not all(
            word in processed_answer
            for word in processed_keyword
        ):

            missing_keywords.append(keyword)

    if final_score < 0.6:

        if is_keyword_stuffing(
            answer,
            keywords,
            reference_answer
        ):

            return (
                "Ответ содержит ключевые слова, но не раскрывает их "
                "связным объяснением."
            )

        if missing_keywords:

            return (
                "Ответ содержит ошибки или противоречия. "
                "Отсутствуют ключевые элементы: "
                + ", ".join(missing_keywords)
            )

        return (
            "Ответ содержит смысловые ошибки "
            "или противоречит эталонному ответу"
        )

    if not missing_keywords:

        return (
            "Ответ содержит все ключевые элементы"
        )

    return (
        "Отсутствуют ключевые элементы: "
        + ", ".join(missing_keywords)
    )


def grade_from_score(score):

    if score >= 0.9:
        return 5

    elif score >= 0.75:
        return 4

    elif score >= 0.6:
        return 3

    return 2


def detect_negation(text):

    negation_words = {
        "не",
        "нет",
        "никогда",
        "ни",
    }

    processed_text = preprocess_text(text)

    for word in processed_text:

        if word in negation_words:
            return True

    return False


def apply_negation_penalty(
    score,
    reference_answer,
    student_answer
):

    reference_negation = detect_negation(
        reference_answer
    )

    student_negation = detect_negation(
        student_answer
    )

    if reference_negation != student_negation:

        score -= 0.3

    if score < 0:
        score = 0

    return round(score, 2)
