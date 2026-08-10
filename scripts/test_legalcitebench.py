import json
from pathlib import Path
from collections import Counter


class LegalCiteBenchTester:

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.data_dir = self.project_root / "data" / "datasets" / "legalcitebench"

        self.cat3_file = (
            self.data_dir / "cat3_citation_error_detection.jsonl"
        )

        self.cat4_file = (
            self.data_dir / "cat4_2_case_verification.jsonl"
        )

    def load_jsonl(self, path):
        records = []

        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    records.append(json.loads(line))

        return records

    def test(self):

        print("=" * 60)
        print("LEGALCITEBENCH DATASET")
        print("=" * 60)

        cat3 = self.load_jsonl(self.cat3_file)
        cat4 = self.load_jsonl(self.cat4_file)

        print(f"\nCAT3 Citation Error Detection")
        print(f"Records : {len(cat3)}")

        cat3_styles = Counter(
            record["qa_style"]
            for record in cat3
        )

        print("Classes :")

        for label, count in cat3_styles.items():
            print(f"  {label}: {count}")

        fake_types = Counter(
            record.get("fake_type")
            for record in cat3
            if record.get("fake_type")
        )

        print("\nFake citation error types:")

        for error_type, count in fake_types.items():
            print(f"  {error_type}: {count}")

        print("\n" + "=" * 60)

        print("CAT4.2 Case Verification")
        print(f"Records : {len(cat4)}")

        cat4_styles = Counter(
            record["qa_style"]
            for record in cat4
        )

        print("Classes :")

        for label, count in cat4_styles.items():
            print(f"  {label}: {count}")

        print("\n" + "=" * 60)

        print("SAMPLE CAT3 RECORD")
        print("=" * 60)

        sample_cat3 = cat3[0]

        print(f"ID          : {sample_cat3['id']}")
        print(f"QA Style    : {sample_cat3['qa_style']}")
        print(f"Legal Angle : {sample_cat3['legal_angle']}")
        print(f"Fake Type   : {sample_cat3.get('fake_type')}")
        print(f"Ground Truth: {sample_cat3['ground_truth']}")

        print("\n" + "=" * 60)

        print("SAMPLE CAT4.2 RECORD")
        print("=" * 60)

        sample_cat4 = cat4[0]

        print(f"ID          : {sample_cat4['id']}")
        print(f"QA Style    : {sample_cat4['qa_style']}")
        print(f"Legal Angle : {sample_cat4['legal_angle']}")
        print(f"Ground Truth: {sample_cat4['ground_truth']}")

        print("\n" + "=" * 60)
        print("LegalCiteBench loaded successfully.")
        print("=" * 60)


if __name__ == "__main__":
    tester = LegalCiteBenchTester()
    tester.test()