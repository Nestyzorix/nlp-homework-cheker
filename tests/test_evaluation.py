import pytest

from app.services.nlp_service import EvaluationConfig
from app.services.nlp_service import keyword_score
from app.services.nlp_service import evaluate_answer
from app.services.nlp_service import get_evaluation_config
from app.services.nlp_service import grade_from_score
from app.services.nlp_service import validate_evaluation_config


REFERENCE = (
    "База данных представляет собой организованную совокупность данных, "
    "которая хранится и обрабатывается с помощью системы управления базами данных."
)

KEYWORDS = [
    "организованная совокупность данных",
    "хранение данных",
    "система управления базами данных",
]


def test_weight_sum_validation():

    with pytest.raises(ValueError):

        validate_evaluation_config(
            EvaluationConfig(
                semantic_weight=0.9,
                keyword_weight=0.3
            )
        )


def test_grade_thresholds():

    config = EvaluationConfig(
        threshold_5=0.85,
        threshold_4=0.70,
        threshold_3=0.50
    )

    assert grade_from_score(0.85, config) == 5
    assert grade_from_score(0.70, config) == 4
    assert grade_from_score(0.50, config) == 3
    assert grade_from_score(0.49, config) == 2


def test_standard_profiles_have_different_weights():

    definition_config = get_evaluation_config("definition")
    process_config = get_evaluation_config("process")
    factual_config = get_evaluation_config("factual")

    assert definition_config.semantic_weight == 0.7
    assert definition_config.keyword_weight == 0.3

    assert process_config.semantic_weight == 0.6
    assert process_config.keyword_weight == 0.4

    assert factual_config.semantic_weight == 0.8
    assert factual_config.keyword_weight == 0.2


def test_fully_correct_answer():

    result = evaluate_answer(
        "База данных - это организованная совокупность данных для хранения в СУБД.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.96,
        keyword_score_value=1.0
    )

    assert result["grade"] == 5
    assert result["corrected_score"] >= 0.85


def test_paraphrased_correct_answer():

    result = evaluate_answer(
        "Это структурированное хранилище информации, управляемое специальной системой.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.88,
        keyword_score_value=0.5
    )

    assert result["grade"] in {4, 5}


def test_partially_correct_answer():

    result = evaluate_answer(
        "База данных нужна для хранения данных.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.68,
        keyword_score_value=0.34
    )

    assert result["grade"] == 3


def test_irrelevant_answer():

    result = evaluate_answer(
        "HTTP используется для передачи запросов между клиентом и сервером.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.20,
        keyword_score_value=0.0
    )

    assert result["grade"] == 2


def test_conflicting_negation_penalty():

    result = evaluate_answer(
        "База данных не хранит данные и не используется системой управления.",
        REFERENCE,
        KEYWORDS,
        "custom",
        {
            "semantic_weight": 0.8,
            "keyword_weight": 0.2,
            "threshold_5": 0.85,
            "threshold_4": 0.70,
            "threshold_3": 0.50,
            "negation_penalty_enabled": True,
            "negation_penalty_value": 0.4,
            "keyword_stuffing_penalty_enabled": False,
        },
        semantic_score_value=0.95,
        keyword_score_value=1.0
    )

    assert any(
        penalty["type"] == "negation"
        for penalty in result["applied_penalties"]
    )
    assert result["corrected_score"] < result["raw_total_score"]


def test_allowed_negation_without_automatic_penalty():

    result = evaluate_answer(
        "SQL не является языком разметки.",
        "SQL не является языком разметки, потому что используется для запросов к базам данных.",
        ["SQL", "язык разметки"],
        semantic_score_value=0.95,
        keyword_score_value=1.0
    )

    assert result["applied_penalties"] == []


def test_low_confidence_negation_phrase_without_penalty():

    result = evaluate_answer(
        "База данных нужна для хранения данных, но про систему управления я не помню.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.70,
        keyword_score_value=0.67
    )

    assert result["applied_penalties"] == []


def test_hyphenated_keyword_is_split_correctly():

    score = keyword_score(
        "Клиент отправляет стандартные HTTP-запросы к ресурсам сервера.",
        [
            "HTTP-методы",
            "ресурсы",
        ]
    )

    assert score >= 0.75


def test_synonym_keyword_match():

    score = keyword_score(
        "Нормализация уменьшает дублирование данных в таблицах.",
        [
            "уменьшение избыточности",
        ]
    )

    assert score >= 0.5


def test_generic_word_does_not_match_whole_keyword():

    score = keyword_score(
        "Ответ просто упоминает данные без объяснения.",
        [
            "целостность данных",
        ]
    )

    assert score < 0.5


def test_keyword_stuffing_penalty():

    result = evaluate_answer(
        "организованная совокупность данных хранение данных система управления базами данных",
        REFERENCE,
        KEYWORDS,
        "custom",
        {
            "semantic_weight": 0.8,
            "keyword_weight": 0.2,
            "threshold_5": 0.85,
            "threshold_4": 0.70,
            "threshold_3": 0.50,
            "negation_penalty_enabled": False,
            "keyword_stuffing_penalty_enabled": True,
            "keyword_stuffing_penalty_value": 0.3,
        },
        semantic_score_value=0.90,
        keyword_score_value=1.0
    )

    assert any(
        penalty["type"] == "keyword_stuffing"
        for penalty in result["applied_penalties"]
    )


def test_custom_config_can_disable_penalties():

    result = evaluate_answer(
        "База данных не хранит данные.",
        REFERENCE,
        KEYWORDS,
        "custom",
        {
            "semantic_weight": 0.8,
            "keyword_weight": 0.2,
            "threshold_5": 0.85,
            "threshold_4": 0.70,
            "threshold_3": 0.50,
            "negation_penalty_enabled": False,
            "keyword_stuffing_penalty_enabled": False,
        },
        semantic_score_value=0.90,
        keyword_score_value=1.0
    )

    assert result["applied_penalties"] == []


def test_algorithm_backward_compatibility_without_config():

    config = get_evaluation_config()

    assert config.semantic_weight == 0.8
    assert config.keyword_weight == 0.2

    result = evaluate_answer(
        "База данных хранит данные.",
        REFERENCE,
        KEYWORDS,
        semantic_score_value=0.70,
        keyword_score_value=0.34
    )

    assert "grade" in result
    assert result["evaluation_profile"] == "factual"
