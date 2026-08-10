import csv
import json
import re
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "stage2"
)

CAT3_INPUT = (
    RESULTS_DIR
    / "cat3_pilot_predictions.jsonl"
)

CAT4_INPUT = (
    RESULTS_DIR
    / "cat4_2_pilot_predictions.jsonl"
)

CAT3_OUTPUT = (
    RESULTS_DIR
    / "cat3_results.csv"
)

CAT4_OUTPUT = (
    RESULTS_DIR
    / "cat4_2_results.csv"
)

SUMMARY_OUTPUT = (
    RESULTS_DIR
    / "stage2_summary.json"
)


def load_jsonl(path):

    records = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def normalize_text(value):

    if value is None:
        return ""

    value = str(value).lower()

    value = value.replace(
        "\u00a0",
        " "
    )

    # Normalize whitespace.
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Remove spaces around punctuation.
    value = re.sub(
        r"\s*,\s*",
        ",",
        value
    )

    value = re.sub(
        r"\s*;\s*",
        ";",
        value
    )

    value = re.sub(
        r"\s*\.\s*",
        ".",
        value
    )

    value = re.sub(
        r"\s+v\.\s+",
        " v. ",
        value
    )

    # Normalize common procedural party labels that do not
    # change the identity of the case.
    value = re.sub(
        r",?\s*(appellant|appellee|appellants|appellees|"
        r"relator|respondent|respondents)\b",
        "",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize_citation(value):

    value = normalize_text(value)

    # Remove surrounding punctuation.
    value = value.strip(
        " \t\n\r.,;:"
    )

    # Normalize common year formatting.
    value = re.sub(
        r"\s*\(\d{4}\)\s*$",
        "",
        value
    )

    return value


def parse_cat3_gold(value):

    """
    Example:

    The citation is incorrect.
    The correct citation is: 3 Cir. 11

    Returns:
        is_correct
        corrected_citation
    """

    text = normalize_text(value)

    if "there is no error" in text:
        return True, None

    match = re.search(
        r"correct citation is:\s*(.+)$",
        text,
        flags=re.IGNORECASE
    )

    corrected = None

    if match:
        corrected = match.group(1).strip()

    return False, corrected


def evaluate_cat3(records):

    results = []

    detection_correct = 0
    error_type_correct = 0
    correction_correct = 0

    for record in records:

        prediction = record["prediction"]

        predicted_correct = bool(
            prediction.get(
                "is_correct",
                False
            )
        )

        predicted_type = normalize_text(
            prediction.get(
                "error_type"
            )
        )

        predicted_correction = (
            normalize_citation(
                prediction.get(
                    "corrected_citation"
                )
            )
        )

        gold_correct, gold_correction = (
            parse_cat3_gold(
                record["ground_truth"]
            )
        )

        gold_type = normalize_text(
            record.get("fake_type")
        )

        detection_match = (
            predicted_correct == gold_correct
        )

        type_match = False

        if not gold_correct:
            type_match = (
                predicted_type == gold_type
            )

        correction_match = False

        if not gold_correct:

            gold_correction = (
                normalize_citation(
                    gold_correction
                )
            )

            correction_match = (
                predicted_correction
                == gold_correction
            )

        if detection_match:
            detection_correct += 1

        if type_match:
            error_type_correct += 1

        if correction_match:
            correction_correct += 1

        results.append({

            "id": record["id"],

            "qa_style":
                record["qa_style"],

            "gold_is_correct":
                gold_correct,

            "predicted_is_correct":
                predicted_correct,

            "detection_correct":
                detection_match,

            "gold_error_type":
                gold_type,

            "predicted_error_type":
                predicted_type,

            "error_type_correct":
                type_match,

            "gold_correction":
                gold_correction,

            "predicted_correction":
                predicted_correction,

            "correction_correct":
                correction_match

        })

    total = len(records)

    fake_records = [
        r for r in results
        if not r["gold_is_correct"]
    ]

    fake_count = len(fake_records)

    return results, {

        "records": total,

        "detection_accuracy":
            detection_correct / total
            if total else 0,

        "error_type_accuracy_on_fake":
            error_type_correct / fake_count
            if fake_count else 0,

        "correction_accuracy_on_fake":
            correction_correct / fake_count
            if fake_count else 0,

        "correct_detections":
            detection_correct,

        "correct_error_types":
            error_type_correct,

        "correct_corrections":
            correction_correct,

        "fake_records":
            fake_count

    }


def parse_cat4_gold(value):

    """
    Converts:

    [
        ["case_name", "..."],
        ["case_cite", "..."],
        ...
    ]

    into a dictionary.
    """

    result = {}

    if isinstance(value, list):

        for item in value:

            if (
                isinstance(item, list)
                and len(item) >= 2
            ):
                result[
                    item[0]
                ] = item[1]

    return result


def evaluate_cat4(records):

    results = []

    verification_correct = 0
    case_name_correct = 0
    citation_correct = 0

    for record in records:

        prediction = record["prediction"]

        predicted_correct = bool(
            prediction.get(
                "is_correct",
                False
            )
        )

        gold = parse_cat4_gold(
            record["ground_truth"]
        )

        gold_name = normalize_text(
            gold.get("case_name")
        )

        gold_cite = normalize_citation(
            gold.get("case_cite")
        )

        predicted_name = normalize_text(
            prediction.get("case_name")
        )

        predicted_cite = normalize_citation(
            prediction.get("case_citation")
        )

        # Determine whether this is a true or fake case.
        is_true = (
            record["qa_style"]
            == "4-2-true"
        )

        gold_is_correct = is_true

        verification_match = (
            predicted_correct
            == gold_is_correct
        )

        name_match = (
            predicted_name
            == gold_name
        )

        citation_match = (
            predicted_cite
            == gold_cite
        )

        if verification_match:
            verification_correct += 1

        if name_match:
            case_name_correct += 1

        if citation_match:
            citation_correct += 1

        results.append({

            "id":
                record["id"],

            "qa_style":
                record["qa_style"],

            "gold_is_correct":
                gold_is_correct,

            "predicted_is_correct":
                predicted_correct,

            "verification_correct":
                verification_match,

            "gold_case_name":
                gold_name,

            "predicted_case_name":
                predicted_name,

            "case_name_correct":
                name_match,

            "gold_case_citation":
                gold_cite,

            "predicted_case_citation":
                predicted_cite,

            "citation_correct":
                citation_match

        })

    total = len(records)

    return results, {

        "records": total,

        "verification_accuracy":
            verification_correct / total
            if total else 0,

        "case_name_accuracy":
            case_name_correct / total
            if total else 0,

        "citation_accuracy":
            citation_correct / total
            if total else 0,

        "correct_verifications":
            verification_correct,

        "correct_case_names":
            case_name_correct,

        "correct_citations":
            citation_correct

    }


def write_csv(path, rows):

    if not rows:
        return

    with open(
        path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)


def main():

    print("=" * 60)
    print("STAGE 2 — PILOT EVALUATION")
    print("=" * 60)

    cat3_records = load_jsonl(
        CAT3_INPUT
    )

    cat4_records = load_jsonl(
        CAT4_INPUT
    )

    print(
        f"\nCAT3 records   : {len(cat3_records)}"
    )

    print(
        f"CAT4.2 records : {len(cat4_records)}"
    )

    cat3_rows, cat3_metrics = (
        evaluate_cat3(
            cat3_records
        )
    )

    cat4_rows, cat4_metrics = (
        evaluate_cat4(
            cat4_records
        )
    )

    write_csv(
        CAT3_OUTPUT,
        cat3_rows
    )

    write_csv(
        CAT4_OUTPUT,
        cat4_rows
    )

    summary = {

        "stage": 2,

        "benchmark":
            "LegalCiteBench",

        "evaluation":
            "pilot",

        "cat3":
            cat3_metrics,

        "cat4_2":
            cat4_metrics

    }

    with open(
        SUMMARY_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=2
        )

    print("\n" + "=" * 60)
    print("CAT3 RESULTS")
    print("=" * 60)

    print(
        f"Detection accuracy       : "
        f"{cat3_metrics['detection_accuracy']:.4f}"
    )

    print(
        f"Error-type accuracy      : "
        f"{cat3_metrics['error_type_accuracy_on_fake']:.4f}"
    )

    print(
        f"Correction accuracy      : "
        f"{cat3_metrics['correction_accuracy_on_fake']:.4f}"
    )

    print("\n" + "=" * 60)
    print("CAT4.2 RESULTS")
    print("=" * 60)

    print(
        f"Verification accuracy    : "
        f"{cat4_metrics['verification_accuracy']:.4f}"
    )

    print(
        f"Case-name accuracy       : "
        f"{cat4_metrics['case_name_accuracy']:.4f}"
    )

    print(
        f"Citation accuracy        : "
        f"{cat4_metrics['citation_accuracy']:.4f}"
    )

    print("\n" + "=" * 60)
    print("FILES SAVED")
    print("=" * 60)

    print(CAT3_OUTPUT)
    print(CAT4_OUTPUT)
    print(SUMMARY_OUTPUT)

    print("\nStage 2 pilot evaluation complete.")


if __name__ == "__main__":
    main()