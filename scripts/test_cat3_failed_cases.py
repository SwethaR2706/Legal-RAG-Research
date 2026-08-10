import json

from src.verification.groq_verifier import GroqCitationVerifier


PREDICTIONS = (
    "results/stage2/cat3_pilot_predictions.jsonl"
)

DATASET = (
    "data/datasets/legalcitebench/"
    "cat3_citation_error_detection.jsonl"
)


def load_predictions():

    records = []

    with open(
        PREDICTIONS,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def load_dataset():

    records = {}

    with open(
        DATASET,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():

                item = json.loads(line)

                records[
                    str(item["id"])
                ] = item

    return records


def main():

    predictions = load_predictions()
    dataset = load_dataset()

    verifier = GroqCitationVerifier()

    failed_true = [
        record
        for record in predictions
        if record["qa_style"] == "3-true"
        and record["prediction"]["is_correct"] is False
    ]

    print("=" * 60)
    print("CAT3 FALSE-POSITIVE RECHECK")
    print("=" * 60)

    for record in failed_true[:5]:

        item = dataset[
            str(record["id"])
        ]

        new_prediction = verifier.verify_cat3(
            item["question"]
        )

        print()
        print(f"ID: {record['id']}")
        print("Gold: TRUE")
        print(
            "Old:",
            record["prediction"]
        )
        print(
            "New:",
            new_prediction
        )


if __name__ == "__main__":
    main()