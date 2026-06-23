import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from app.services.nlp_service import evaluate_answer
from app.services.nlp_service import keyword_score
from app.services.nlp_service import semantic_similarity


WEIGHT_VARIANTS = [
    (1.0, 0.0),
    (0.8, 0.2),
    (0.7, 0.3),
    (0.5, 0.5),
    (0.0, 1.0),
]

THRESHOLD_SCALES = {
    "Scale A": {
        "threshold_5": 0.85,
        "threshold_4": 0.70,
        "threshold_3": 0.50,
    },
    "Scale B": {
        "threshold_5": 0.80,
        "threshold_4": 0.65,
        "threshold_3": 0.45,
    },
    "Scale C": {
        "threshold_5": 0.90,
        "threshold_4": 0.75,
        "threshold_3": 0.55,
    },
}

PENALTY_VARIANTS = [
    ("without_penalties", False),
    ("with_penalties", True),
]

ANSWER_TYPES = [
    "fully_correct",
    "paraphrased_correct",
    "partially_correct",
    "incorrect_or_negated",
    "irrelevant",
]


def default_dataset_path():

    return (
        Path(__file__)
        .resolve()
        .parents[1]
        / "data"
        / "evaluation_cases.json"
    )


def load_cases(path):

    with Path(path).open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_config(
    semantic_weight,
    keyword_weight,
    scale,
    penalties_enabled
):

    return {
        "semantic_weight": semantic_weight,
        "keyword_weight": keyword_weight,
        "threshold_5": scale["threshold_5"],
        "threshold_4": scale["threshold_4"],
        "threshold_3": scale["threshold_3"],
        "negation_penalty_enabled": penalties_enabled,
        "keyword_stuffing_penalty_enabled": penalties_enabled,
    }


def precompute_scores(cases):

    prepared_cases = []

    for case in cases:

        semantic = semantic_similarity(
            case["student_answer"],
            case["reference_answer"]
        )

        keyword = keyword_score(
            case["student_answer"],
            case["keywords"]
        )

        prepared_case = dict(case)
        prepared_case["semantic_score"] = semantic
        prepared_case["keyword_score"] = keyword
        prepared_cases.append(prepared_case)

    return prepared_cases


def evaluate_configuration(
    cases,
    config_name,
    semantic_weight,
    keyword_weight,
    scale_name,
    scale,
    penalty_name,
    penalties_enabled
):

    config = build_config(
        semantic_weight,
        keyword_weight,
        scale,
        penalties_enabled
    )

    details = []

    for case in cases:

        result = evaluate_answer(
            case["student_answer"],
            case["reference_answer"],
            case["keywords"],
            "custom",
            config,
            semantic_score_value=case["semantic_score"],
            keyword_score_value=case["keyword_score"]
        )

        expected_grade = case["expected_grade"]
        predicted_grade = result["grade"]
        absolute_error = abs(
            expected_grade - predicted_grade
        )

        details.append({
            "configuration": config_name,
            "scale": scale_name,
            "penalties": penalty_name,
            "case_id": case["id"],
            "question": case["question"],
            "answer_type": case["answer_type"],
            "expected_grade": expected_grade,
            "predicted_grade": predicted_grade,
            "absolute_error": absolute_error,
            "semantic_score": result["semantic_score"],
            "keyword_score": result["keyword_score"],
            "raw_total_score": result["raw_total_score"],
            "corrected_score": result["corrected_score"],
            "feedback": result["feedback"],
            "applied_penalties": json.dumps(
                result["applied_penalties"],
                ensure_ascii=False
            ),
        })

    return details


def summarize_details(details):

    count = len(details)
    exact_matches = sum(
        1
        for detail in details
        if detail["absolute_error"] == 0
    )
    one_point_errors = sum(
        1
        for detail in details
        if detail["absolute_error"] == 1
    )
    more_than_one_point_errors = sum(
        1
        for detail in details
        if detail["absolute_error"] > 1
    )
    mae = sum(
        detail["absolute_error"]
        for detail in details
    ) / count
    max_absolute_error = max(
        detail["absolute_error"]
        for detail in details
    )

    summary = {
        "configuration": details[0]["configuration"],
        "scale": details[0]["scale"],
        "penalties": details[0]["penalties"],
        "case_count": count,
        "exact_matches": exact_matches,
        "exact_match_rate": round(
            exact_matches / count,
            4
        ),
        "one_point_errors": one_point_errors,
        "more_than_one_point_errors": more_than_one_point_errors,
        "mae": round(
            mae,
            4
        ),
        "max_absolute_error": max_absolute_error,
    }

    details_by_type = defaultdict(list)

    for detail in details:

        details_by_type[detail["answer_type"]].append(detail)

    for answer_type in ANSWER_TYPES:

        type_details = details_by_type[answer_type]

        if not type_details:

            continue

        type_count = len(type_details)
        type_exact = sum(
            1
            for detail in type_details
            if detail["absolute_error"] == 0
        )
        type_mae = sum(
            detail["absolute_error"]
            for detail in type_details
        ) / type_count

        summary[f"{answer_type}_count"] = type_count
        summary[f"{answer_type}_exact_matches"] = type_exact
        summary[f"{answer_type}_mae"] = round(
            type_mae,
            4
        )

    return summary


def write_csv(path, rows):

    if not rows:

        return

    fieldnames = []

    for row in rows:

        for key in row.keys():

            if key not in fieldnames:

                fieldnames.append(key)

    with Path(path).open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)


def print_summary(summary_rows):

    header = (
        "configuration",
        "scale",
        "penalties",
        "exact",
        "rate",
        "mae",
        "max_error",
    )

    print(
        f"{header[0]:<18} {header[1]:<8} {header[2]:<18} "
        f"{header[3]:<7} {header[4]:<8} {header[5]:<8} {header[6]}"
    )
    print("-" * 86)

    for row in summary_rows:

        print(
            f"{row['configuration']:<18} "
            f"{row['scale']:<8} "
            f"{row['penalties']:<18} "
            f"{row['exact_matches']:<7} "
            f"{row['exact_match_rate']:<8} "
            f"{row['mae']:<8} "
            f"{row['max_absolute_error']}"
        )


def find_best_configuration(summary_rows):

    return sorted(
        summary_rows,
        key=lambda row: (
            row["mae"],
            -row["exact_matches"]
        )
    )[0]


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Compare NLP homework checker weights, thresholds and penalties."
        )
    )
    parser.add_argument(
        "--dataset",
        default=str(default_dataset_path()),
        help="Path to JSON dataset with evaluation cases."
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for evaluation_summary.csv and evaluation_details.csv."
    )

    args = parser.parse_args()

    cases = precompute_scores(
        load_cases(args.dataset)
    )

    all_details = []
    summary_rows = []

    for semantic_weight, keyword_weight in WEIGHT_VARIANTS:

        for scale_name, scale in THRESHOLD_SCALES.items():

            for penalty_name, penalties_enabled in PENALTY_VARIANTS:

                config_name = (
                    f"semantic_{semantic_weight}_keyword_{keyword_weight}"
                )

                details = evaluate_configuration(
                    cases,
                    config_name,
                    semantic_weight,
                    keyword_weight,
                    scale_name,
                    scale,
                    penalty_name,
                    penalties_enabled
                )

                all_details.extend(details)
                summary_rows.append(
                    summarize_details(details)
                )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    summary_path = output_dir / "evaluation_summary.csv"
    details_path = output_dir / "evaluation_details.csv"

    write_csv(
        summary_path,
        summary_rows
    )
    write_csv(
        details_path,
        all_details
    )

    print_summary(summary_rows)

    best = find_best_configuration(summary_rows)

    print()
    print(
        "Рекомендация по результатам эксперимента: "
        f"{best['configuration']}, {best['scale']}, {best['penalties']} "
        f"(MAE={best['mae']}, точных совпадений={best['exact_matches']})."
    )
    print(
        "Рабочая конфигурация системы автоматически не изменялась."
    )
    print(
        f"CSV сохранены: {summary_path}, {details_path}"
    )


if __name__ == "__main__":

    main()
