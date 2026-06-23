import argparse
import csv
import json
from pathlib import Path

from app.services.nlp_service import evaluate_answer


ENGLISH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "between",
    "by",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "one",
    "or",
    "that",
    "the",
    "there",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "you",
}


def normalize_gap(value):

    return (value or "").strip()


def has_gap(row):

    return bool(
        normalize_gap(
            row.get("gap")
        )
    )


def extract_keywords(model_answer, max_keywords=6):

    words = []

    for raw_word in model_answer.lower().replace("/", " ").split():

        word = "".join(
            char
            for char in raw_word
            if char.isalnum()
        )

        if (
            len(word) < 4
            or word in ENGLISH_STOPWORDS
        ):

            continue

        if word not in words:

            words.append(word)

    return words[:max_keywords]


def load_rows(path, limit=None):

    with Path(path).open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if limit:

        return rows[:limit]

    return rows


def evaluate_rows(rows, dataset_name):

    details = []

    for index, row in enumerate(rows, start=1):

        question = row["question_text"]
        student_answer = row["student_answer"]
        model_answer = row["model_answer"]
        keywords = extract_keywords(model_answer)

        result = evaluate_answer(
            student_answer,
            model_answer,
            keywords,
            "factual"
        )

        expected_has_gap = has_gap(row)
        predicted_has_gap = result["grade"] < 5

        details.append({
            "dataset": dataset_name,
            "row_number": index,
            "student_answer_id": row.get("student_answer_id"),
            "question_paper": row.get("question_paper"),
            "question": question,
            "model_answer": model_answer,
            "student_answer": student_answer,
            "gap": normalize_gap(row.get("gap")),
            "keywords": ", ".join(keywords),
            "semantic_score": result["semantic_score"],
            "keyword_score": result["keyword_score"],
            "raw_total_score": result["raw_total_score"],
            "corrected_score": result["corrected_score"],
            "grade": result["grade"],
            "feedback": result["feedback"],
            "applied_penalties": json.dumps(
                result["applied_penalties"],
                ensure_ascii=False
            ),
            "expected_has_gap": expected_has_gap,
            "predicted_has_gap": predicted_has_gap,
            "gap_detection_match": expected_has_gap == predicted_has_gap,
        })

    return details


def summarize(details):

    total = len(details)
    complete_rows = [
        row
        for row in details
        if not row["expected_has_gap"]
    ]
    gap_rows = [
        row
        for row in details
        if row["expected_has_gap"]
    ]
    matches = [
        row
        for row in details
        if row["gap_detection_match"]
    ]
    high_for_complete = [
        row
        for row in complete_rows
        if row["grade"] >= 4
    ]
    not_perfect_for_gap = [
        row
        for row in gap_rows
        if row["grade"] < 5
    ]
    average_grade = sum(
        row["grade"]
        for row in details
    ) / total

    return {
        "dataset": details[0]["dataset"] if details else "",
        "total": total,
        "without_gap": len(complete_rows),
        "with_gap": len(gap_rows),
        "gap_detection_matches": len(matches),
        "gap_detection_match_rate": round(
            len(matches) / total,
            4
        ) if total else 0,
        "complete_answers_grade_4_or_5": len(high_for_complete),
        "complete_answers_grade_4_or_5_rate": round(
            len(high_for_complete) / len(complete_rows),
            4
        ) if complete_rows else 0,
        "gap_answers_below_5": len(not_perfect_for_gap),
        "gap_answers_below_5_rate": round(
            len(not_perfect_for_gap) / len(gap_rows),
            4
        ) if gap_rows else 0,
        "average_grade": round(
            average_grade,
            4
        ) if total else 0,
    }


def write_csv(path, rows):

    if not rows:

        return

    fieldnames = []

    for row in rows:

        for key in row:

            if key not in fieldnames:

                fieldnames.append(key)

    with Path(path).open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)


def print_summary(summary_rows):

    print(
        "dataset total without_gap with_gap match_rate complete_high_rate "
        "gap_below_5_rate avg_grade"
    )
    print("-" * 96)

    for row in summary_rows:

        print(
            f"{row['dataset']} {row['total']} {row['without_gap']} "
            f"{row['with_gap']} {row['gap_detection_match_rate']} "
            f"{row['complete_answers_grade_4_or_5_rate']} "
            f"{row['gap_answers_below_5_rate']} {row['average_grade']}"
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the algorithm on external gap-annotated short answer datasets."
        )
    )
    parser.add_argument(
        "--input-dir",
        default="external_datasets",
        help="Directory with UNT.csv, SciEntsBank.csv and Beetle.csv."
    )
    parser.add_argument(
        "--output-dir",
        default="external_evaluation_results",
        help="Directory for external evaluation CSV files."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional row limit per dataset for quick checks."
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    all_details = []
    summary_rows = []

    for csv_path in sorted(input_dir.glob("*.csv")):

        rows = load_rows(
            csv_path,
            args.limit
        )

        details = evaluate_rows(
            rows,
            csv_path.stem
        )

        all_details.extend(details)
        summary_rows.append(
            summarize(details)
        )

    write_csv(
        output_dir / "external_gap_summary.csv",
        summary_rows
    )
    write_csv(
        output_dir / "external_gap_details.csv",
        all_details
    )

    print_summary(summary_rows)
    print()
    print(
        "Важно: gap-разметка показывает отсутствующие элементы ответа, "
        "а не точную оценку 2-5."
    )


if __name__ == "__main__":

    main()
