import json

from src.verification.groq_verifier import GroqCitationVerifier


def load_first(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.loads(file.readline())


def main():

    verifier = GroqCitationVerifier()

    cat3 = load_first(
        "data/datasets/legalcitebench/"
        "cat3_citation_error_detection.jsonl"
    )

    print("=" * 60)
    print("CAT3 TEST")
    print("=" * 60)

    prediction = verifier.verify_cat3(
        cat3["question"]
    )

    print(json.dumps(
        prediction,
        indent=2,
        ensure_ascii=False
    ))

    print()
    print("Gold:")
    print(cat3["ground_truth"])

    print()
    print("=" * 60)
    print("CAT4.2 TEST")
    print("=" * 60)

    cat4 = load_first(
        "data/datasets/legalcitebench/"
        "cat4_2_case_verification.jsonl"
    )

    prediction = verifier.verify_cat4_2(
        cat4["question"]
    )

    print(json.dumps(
        prediction,
        indent=2,
        ensure_ascii=False
    ))

    print()
    print("Gold:")
    print(cat4["ground_truth"])


if __name__ == "__main__":
    main()