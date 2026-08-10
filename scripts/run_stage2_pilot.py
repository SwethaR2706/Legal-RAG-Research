import json
from pathlib import Path

from src.verification.groq_verifier import GroqCitationVerifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "datasets"
    / "legalcitebench"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "stage2"
)

CAT3_FILE = DATA_DIR / "cat3_citation_error_detection.jsonl"
CAT4_FILE = DATA_DIR / "cat4_2_case_verification.jsonl"

CAT3_OUTPUT = RESULTS_DIR / "cat3_pilot_predictions.jsonl"
CAT4_OUTPUT = RESULTS_DIR / "cat4_2_pilot_predictions.jsonl"


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def save_prediction(path, record):

    with open(path, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )


def already_completed(path):

    if not path.exists():
        return set()

    completed = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)
            completed.add(str(record["id"]))

    return completed


def select_balanced(records, total=40):

    true_records = [
        r for r in records
        if r["qa_style"] in ("3-true", "4-2-true")
    ]

    fake_records = [
        r for r in records
        if r["qa_style"] in ("3-fake", "4-2-fake")
    ]

    half = total // 2

    return (
        true_records[:half]
        + fake_records[:half]
    )


def run_cat3(verifier):

    records = load_jsonl(CAT3_FILE)

    selected = select_balanced(records, 40)

    completed = already_completed(CAT3_OUTPUT)

    print("=" * 60)
    print("CAT3 PILOT")
    print("=" * 60)
    print(f"Selected : {len(selected)}")
    print(f"Completed: {len(completed)}")
    print()

    for index, record in enumerate(selected, 1):

        record_id = str(record["id"])

        if record_id in completed:
            continue

        print(
            f"CAT3 {index}/{len(selected)} "
            f"| ID {record_id}",
            flush=True
        )

        try:

            prediction = verifier.verify_cat3(
                record["question"]
            )

            output = {
                "id": record_id,
                "qa_style": record["qa_style"],
                "legal_angle": record.get("legal_angle"),
                "fake_type": record.get("fake_type"),
                "prediction": prediction,
                "ground_truth": record["ground_truth"]
            }

            save_prediction(
                CAT3_OUTPUT,
                output
            )

            print("  Saved.", flush=True)

        except Exception as error:

            print(
                f"  ERROR: {error}",
                flush=True
            )


def run_cat4(verifier):

    records = load_jsonl(CAT4_FILE)

    selected = select_balanced(records, 40)

    completed = already_completed(CAT4_OUTPUT)

    print("=" * 60)
    print("CAT4.2 PILOT")
    print("=" * 60)
    print(f"Selected : {len(selected)}")
    print(f"Completed: {len(completed)}")
    print()

    for index, record in enumerate(selected, 1):

        record_id = str(record["id"])

        if record_id in completed:
            continue

        print(
            f"CAT4.2 {index}/{len(selected)} "
            f"| ID {record_id}",
            flush=True
        )

        try:

            prediction = verifier.verify_cat4_2(
                record["question"]
            )

            output = {
                "id": record_id,
                "qa_style": record["qa_style"],
                "legal_angle": record.get("legal_angle"),
                "prediction": prediction,
                "ground_truth": record["ground_truth"],
                "wrong_case_cited":
                    record.get("wrong_case_cited")
            }

            save_prediction(
                CAT4_OUTPUT,
                output
            )

            print("  Saved.", flush=True)

        except Exception as error:

            print(
                f"  ERROR: {error}",
                flush=True
            )


def main():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    verifier = GroqCitationVerifier()

    run_cat3(verifier)

    run_cat4(verifier)

    print()
    print("=" * 60)
    print("STAGE 2 PILOT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()