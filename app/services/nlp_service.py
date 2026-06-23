from dataclasses import asdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.preprocessing import normalize_word
from app.utils.preprocessing import preprocess_text


model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


SUPPORTED_PROFILES = {
    "definition",
    "process",
    "factual",
    "custom",
}


SYNONYM_GROUPS = [
    {
        "данные",
        "информация",
        "сведения",
    },
    {
        "избыточность",
        "дублирование",
    },
    {
        "хранение",
        "хранилище",
        "сохранять",
    },
    {
        "организованный",
        "структурированный",
    },
    {
        "интерфейс",
        "способ",
        "взаимодействие",
    },
    {
        "программный",
        "приложение",
        "программа",
    },
    {
        "метод",
        "запрос",
        "обращение",
    },
    {
        "ресурс",
        "объект",
    },
    {
        "ответ",
        "результат",
    },
    {
        "генерация",
        "создание",
        "создавать",
    },
    {
        "понимание",
        "смысл",
    },
    {
        "анализ",
        "извлекать",
        "классифицировать",
    },
]


GENERIC_KEYWORD_LEMMAS = {
    "данные",
    "информация",
    "текст",
    "язык",
    "система",
    "программа",
    "приложение",
}


LEMMA_EQUIVALENTS = {}

for synonym_group in SYNONYM_GROUPS:

    for lemma in synonym_group:

        LEMMA_EQUIVALENTS[lemma] = synonym_group


@dataclass(frozen=True)
class EvaluationConfig:

    semantic_weight: float = 0.8
    keyword_weight: float = 0.2
    threshold_5: float = 0.85
    threshold_4: float = 0.70
    threshold_3: float = 0.50
    negation_penalty_enabled: bool = True
    negation_penalty_value: float = 0.30
    keyword_stuffing_penalty_enabled: bool = True
    keyword_stuffing_penalty_value: float = 0.25

    def to_dict(self):

        return asdict(self)


PROFILE_CONFIGS = {
    "definition": EvaluationConfig(
        semantic_weight=0.7,
        keyword_weight=0.3
    ),
    "process": EvaluationConfig(
        semantic_weight=0.6,
        keyword_weight=0.4
    ),
    "factual": EvaluationConfig(),
}


def clamp_score(value):

    return max(
        0,
        min(
            1,
            value
        )
    )


def validate_evaluation_config(config: EvaluationConfig):

    weights = [
        config.semantic_weight,
        config.keyword_weight,
    ]

    thresholds = [
        config.threshold_5,
        config.threshold_4,
        config.threshold_3,
    ]

    for weight in weights:

        if weight < 0 or weight > 1:

            raise ValueError(
                "Вес должен находиться в диапазоне от 0 до 1"
            )

    if abs(config.semantic_weight + config.keyword_weight - 1) > 0.001:

        raise ValueError(
            "Сумма весов семантики и ключевых слов должна быть равна 1"
        )

    for threshold in thresholds:

        if threshold < 0 or threshold > 1:

            raise ValueError(
                "Порог оценки должен находиться в диапазоне от 0 до 1"
            )

    if not (
        config.threshold_5
        > config.threshold_4
        > config.threshold_3
    ):

        raise ValueError(
            "Пороги должны удовлетворять условию: 5 > 4 > 3"
        )

    if config.negation_penalty_value < 0 or config.negation_penalty_value > 1:

        raise ValueError(
            "Штраф за отрицание должен находиться в диапазоне от 0 до 1"
        )

    if (
        config.keyword_stuffing_penalty_value < 0
        or config.keyword_stuffing_penalty_value > 1
    ):

        raise ValueError(
            "Штраф за перечисление ключевых слов должен находиться в диапазоне от 0 до 1"
        )


def _read_config_value(source, key, default):

    if source is None:

        return default

    if isinstance(source, dict):

        value = source.get(key)

    else:

        value = getattr(
            source,
            key,
            None
        )

    if value is None:

        return default

    return value


def get_evaluation_config(
    evaluation_profile="factual",
    custom_config=None
):

    profile = evaluation_profile or "factual"

    if profile not in SUPPORTED_PROFILES:

        raise ValueError(
            "Неподдерживаемый профиль оценивания"
        )

    if profile != "custom":

        config = PROFILE_CONFIGS.get(
            profile,
            PROFILE_CONFIGS["factual"]
        )

        validate_evaluation_config(config)

        return config

    base_config = PROFILE_CONFIGS["factual"]

    config = EvaluationConfig(
        semantic_weight=float(
            _read_config_value(
                custom_config,
                "semantic_weight",
                base_config.semantic_weight
            )
        ),
        keyword_weight=float(
            _read_config_value(
                custom_config,
                "keyword_weight",
                base_config.keyword_weight
            )
        ),
        threshold_5=float(
            _read_config_value(
                custom_config,
                "threshold_5",
                base_config.threshold_5
            )
        ),
        threshold_4=float(
            _read_config_value(
                custom_config,
                "threshold_4",
                base_config.threshold_4
            )
        ),
        threshold_3=float(
            _read_config_value(
                custom_config,
                "threshold_3",
                base_config.threshold_3
            )
        ),
        negation_penalty_enabled=bool(
            _read_config_value(
                custom_config,
                "negation_penalty_enabled",
                base_config.negation_penalty_enabled
            )
        ),
        negation_penalty_value=float(
            _read_config_value(
                custom_config,
                "negation_penalty_value",
                base_config.negation_penalty_value
            )
        ),
        keyword_stuffing_penalty_enabled=bool(
            _read_config_value(
                custom_config,
                "keyword_stuffing_penalty_enabled",
                base_config.keyword_stuffing_penalty_enabled
            )
        ),
        keyword_stuffing_penalty_value=float(
            _read_config_value(
                custom_config,
                "keyword_stuffing_penalty_value",
                base_config.keyword_stuffing_penalty_value
            )
        ),
    )

    validate_evaluation_config(config)

    return config


@lru_cache(maxsize=2048)
def semantic_similarity(answer, reference):

    embeddings = model.encode([
        answer,
        reference
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(
        float(similarity),
        2
    )


def keyword_score(answer, keywords):

    keyword_matches = analyze_keyword_matches(
        answer,
        keywords
    )

    if not keyword_matches:

        return 0

    score = sum(
        match["score"]
        for match in keyword_matches
    ) / len(keyword_matches)

    return round(
        score,
        2
    )


def expand_lemmas(lemmas):

    expanded_lemmas = set(lemmas)

    for lemma in lemmas:

        expanded_lemmas.update(
            LEMMA_EQUIVALENTS.get(
                lemma,
                set()
            )
        )

    return expanded_lemmas


def keyword_match_score(answer, keyword):

    processed_answer = expand_lemmas(
        preprocess_text(answer)
    )

    processed_keyword = preprocess_text(keyword)

    if not processed_keyword:

        return 0

    matched_keyword_lemmas = [
        word
        for word in processed_keyword
        if word in processed_answer
    ]

    lemma_matches = len(matched_keyword_lemmas)

    lemma_coverage = lemma_matches / len(processed_keyword)

    if lemma_coverage >= 0.8:

        return 1

    has_specific_match = any(
        lemma not in GENERIC_KEYWORD_LEMMAS
        for lemma in matched_keyword_lemmas
    )

    if (
        lemma_coverage >= 0.67
        and has_specific_match
    ):

        return 0.75

    if (
        lemma_coverage >= 0.5
        and len(processed_keyword) >= 3
        and has_specific_match
    ):

        return 0.6

    semantic_match = semantic_similarity(
        keyword,
        answer
    )

    if (
        semantic_match >= 0.72
        and has_specific_match
    ):

        return 0.75

    if (
        semantic_match >= 0.62
        and has_specific_match
    ):

        return max(
            0.5,
            lemma_coverage
        )

    if (
        not has_specific_match
        and lemma_coverage < 0.8
    ):

        return min(
            0.4,
            round(
                lemma_coverage,
                2
            )
        )

    return round(
        lemma_coverage,
        2
    )


def analyze_keyword_matches(answer, keywords):

    keyword_matches = []

    for keyword in keywords:

        processed_keyword = preprocess_text(keyword)

        if not processed_keyword:

            continue

        score = keyword_match_score(
            answer,
            keyword
        )

        keyword_matches.append({
            "keyword": keyword,
            "score": score,
            "is_found": score >= 0.5
        })

    return keyword_matches


def analyze_keywords(answer, keywords):

    keyword_matches = analyze_keyword_matches(
        answer,
        keywords
    )

    found_keywords = []
    missing_keywords = []

    for match in keyword_matches:

        if match["is_found"]:

            found_keywords.append(
                match["keyword"]
            )

        else:

            missing_keywords.append(
                match["keyword"]
            )

    return (
        found_keywords,
        missing_keywords
    )


def final_score(
    semantic_score,
    keyword_score_value,
    config=None
):

    effective_config = config or get_evaluation_config()

    result = (
        effective_config.semantic_weight * semantic_score
        + effective_config.keyword_weight * keyword_score_value
    )

    return round(
        result,
        2
    )


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


NEGATION_WORDS = {
    "не",
    "нет",
    "никогда",
    "ни",
}

NON_CONTRADICTING_NEGATION_FOLLOWERS = {
    "знать",
    "помнить",
    "понимать",
    "уверенный",
    "уверен",
    "мочь",
    "смочь",
}

LOW_CONTENT_NEGATION_FOLLOWERS = {
    "только",
    "очень",
    "совсем",
}


def _tokenize_for_negation(text):

    words = re.findall(
        r"[а-яёa-z0-9]+",
        text.lower()
    )

    normalized_words = []

    for word in words:

        if word in NEGATION_WORDS:

            normalized_words.append(word)

        else:

            normalized_words.append(
                normalize_word(word)
            )

    return normalized_words


def get_negation_contexts(text):

    words = _tokenize_for_negation(text)
    contexts = []

    for index, word in enumerate(words):

        if word not in NEGATION_WORDS:

            continue

        window = [
            word
            for word in words[index + 1:index + 5]
            if word not in NEGATION_WORDS
        ]

        if not window:

            continue

        first_meaningful_word = window[0]

        if first_meaningful_word in NON_CONTRADICTING_NEGATION_FOLLOWERS:

            continue

        if first_meaningful_word in LOW_CONTENT_NEGATION_FOLLOWERS:

            continue

        context = set(window)

        contexts.append(context)

    return contexts


def detect_negation(text):

    return bool(
        get_negation_contexts(text)
    )


def has_conflicting_negation(
    reference_answer,
    student_answer
):

    student_contexts = get_negation_contexts(
        student_answer
    )

    if not student_contexts:

        return False

    reference_contexts = get_negation_contexts(
        reference_answer
    )

    if not reference_contexts:

        return True

    for student_context in student_contexts:

        matching_reference_context = any(
            student_context
            and reference_context
            and student_context.intersection(reference_context)
            for reference_context in reference_contexts
        )

        if not matching_reference_context:

            return True

    return False


def apply_negation_penalty(
    score,
    reference_answer,
    student_answer,
    config=None
):

    effective_config = config or get_evaluation_config()

    if not effective_config.negation_penalty_enabled:

        return round(
            score,
            2
        )

    if has_conflicting_negation(
        reference_answer,
        student_answer
    ):

        score -= effective_config.negation_penalty_value

    return round(
        clamp_score(score),
        2
    )


def apply_keyword_stuffing_penalty(
    score,
    answer,
    keywords,
    reference_answer=None,
    config=None
):

    effective_config = config or get_evaluation_config()

    if not effective_config.keyword_stuffing_penalty_enabled:

        return round(
            score,
            2
        )

    if is_keyword_stuffing(
        answer,
        keywords,
        reference_answer
    ):

        score -= effective_config.keyword_stuffing_penalty_value

    return round(
        clamp_score(score),
        2
    )


def grade_from_score(score, config=None):

    effective_config = config or get_evaluation_config()

    if score >= effective_config.threshold_5:

        return 5

    if score >= effective_config.threshold_4:

        return 4

    if score >= effective_config.threshold_3:

        return 3

    return 2


def generate_feedback(
    answer,
    keywords,
    final_score_value,
    reference_answer=None,
    found_keywords=None,
    missing_keywords=None,
    applied_penalties=None
):

    if found_keywords is None or missing_keywords is None:

        found_keywords, missing_keywords = analyze_keywords(
            answer,
            keywords
        )

    applied_penalties = applied_penalties or []

    if applied_penalties:

        penalty_reasons = "; ".join(
            penalty["reason"]
            if isinstance(penalty, dict)
            else str(penalty)
            for penalty in applied_penalties
        )

        return (
            "Ответ требует дополнительной проверки: "
            + penalty_reasons
        )

    if final_score_value < 0.5:

        if missing_keywords:

            return (
                "Ответ содержит ошибки или противоречия. "
                "Отсутствуют ключевые элементы: "
                + ", ".join(missing_keywords)
            )

        return (
            "Ответ существенно не соответствует эталонному ответу"
        )

    if not missing_keywords:

        return (
            "Ответ содержит все ключевые элементы"
        )

    return (
        "Отсутствуют ключевые элементы: "
        + ", ".join(missing_keywords)
    )


def evaluate_answer(
    student_answer,
    reference_answer,
    keywords,
    evaluation_profile="factual",
    custom_config=None,
    semantic_score_value=None,
    keyword_score_value=None
):

    profile = evaluation_profile or "factual"

    config = get_evaluation_config(
        profile,
        custom_config
    )

    semantic = (
        semantic_score_value
        if semantic_score_value is not None
        else semantic_similarity(
            student_answer,
            reference_answer
        )
    )

    found_keywords, missing_keywords = analyze_keywords(
        student_answer,
        keywords
    )

    keyword = (
        keyword_score_value
        if keyword_score_value is not None
        else keyword_score(
            student_answer,
            keywords
        )
    )

    raw_total = final_score(
        semantic,
        keyword,
        config
    )

    applied_penalties: list[dict[str, Any]] = []
    total_penalty = 0

    if (
        config.negation_penalty_enabled
        and has_conflicting_negation(
            reference_answer,
            student_answer
        )
    ):

        applied_penalties.append({
            "type": "negation",
            "value": config.negation_penalty_value,
            "reason": (
                "Обнаружено отрицание, которое может изменять смысл "
                "утверждения относительно эталонного ответа."
            ),
        })

        total_penalty += config.negation_penalty_value

    if (
        config.keyword_stuffing_penalty_enabled
        and is_keyword_stuffing(
            student_answer,
            keywords,
            reference_answer
        )
    ):

        applied_penalties.append({
            "type": "keyword_stuffing",
            "value": config.keyword_stuffing_penalty_value,
            "reason": (
                "Ответ похож на формальное перечисление ключевых слов "
                "без достаточного раскрытия темы."
            ),
        })

        total_penalty += config.keyword_stuffing_penalty_value

    corrected = round(
        clamp_score(
            raw_total - total_penalty
        ),
        2
    )

    grade = grade_from_score(
        corrected,
        config
    )

    feedback = generate_feedback(
        student_answer,
        keywords,
        corrected,
        reference_answer,
        found_keywords,
        missing_keywords,
        applied_penalties
    )

    return {
        "semantic_score": round(float(semantic), 2),
        "keyword_score": round(float(keyword), 2),
        "raw_total_score": raw_total,
        "corrected_score": corrected,
        "final_score": corrected,
        "grade": grade,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "applied_penalties": applied_penalties,
        "feedback": feedback,
        "evaluation_profile": profile,
        "evaluation_config": config.to_dict(),
    }
