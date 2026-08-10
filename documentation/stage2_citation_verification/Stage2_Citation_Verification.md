# Stage 2 — Legal Citation Verification

## 1. Objective

Stage 2 evaluates the legal verification component of the proposed
Legal RAG system using a publicly available legal benchmark.

The objective is to determine whether a language-model-based verifier
can identify incorrect legal citations and verify whether a cited case
is an appropriate legal authority.

Stage 2 is intentionally evaluated independently from the retrieval
evaluation performed in Stage 1.

The evaluation therefore focuses on **legal citation and case-authority
verification**, rather than retrieval quality or end-to-end answer
generation.

---

## 2. Benchmark

### LegalCiteBench

The Stage 2 evaluation uses **LegalCiteBench**, a benchmark containing
multiple legal citation and case-related tasks.

Two categories were selected for this study:

| Category | Task | Purpose |
|---|---|---|
| CAT3 | Citation Error Detection | Detect whether a citation contains an error and identify the erroneous component |
| CAT4.2 | Case Verification | Determine whether the cited case is the correct authority for the described legal proposition |

The benchmark data are stored locally under:

data/datasets/legalcitebench/

Relevant files:

cat3_citation_error_detection.jsonl
cat4_2_case_verification.jsonl

# 3. Stage 2 Architecture

The Stage 2 verification pipeline is independent of the retrieval
pipeline.

LegalCiteBench Record

        |
        v
   Verification
      Model
      
        |
        v
 Structured JSON
   Prediction
   
        |
        v
 Deterministic
   Evaluation
   
        |
        v
 Metrics + CSV

The model receives the benchmark question/legal analysis and produces
a structured prediction.

Gold annotations are not provided to the model during prediction.

They are used only after prediction during the deterministic
evaluation stage.

# 4. Verification Model

The pilot uses a Groq-hosted large language model through the Groq API.

The implementation is located at:

src/verification/groq_verifier.py

The verifier produces structured JSON predictions.

For CAT3, the output contains:

{
  "is_correct": true,
  "error_type": null,
  "corrected_citation": null
}

For an erroneous citation, the verifier may instead return:

{
  "is_correct": false,
  "error_type": "page",
  "corrected_citation": "..."
}

For CAT4.2, the output contains:

{
  "is_correct": true,
  "case_name": "...",
  "case_citation": "..."
}

# 5. CAT3 — Citation Error Detection
# 5.1 Task

CAT3 contains both valid and deliberately corrupted legal citations.

The verifier must determine:

Whether the citation is correct.
If incorrect, which citation component contains the error.
The corresponding corrected citation component.

The benchmark distinguishes the following error types:

Page
Volume
Reporter series

The evaluation therefore separates general citation-error detection
from precise error-type classification and citation correction.

# 5.2 Pilot Configuration

A balanced pilot sample of 40 CAT3 records was evaluated:

| Category  | Number of records |
| --------- | ----------------: |
| 3-true    |                20 |
| 3-fake    |                20 |
| **Total** |            **40** |


The pilot predictions are preserved in:

results/stage2/cat3_pilot_predictions.jsonl

The evaluated results are preserved in:

results/stage2/cat3_results.csv

# 5.3 CAT3 Results
Metric	Result
Citation error detection accuracy	62.5%
Error-type accuracy on erroneous citations	10.0%
Citation correction accuracy on erroneous citations	0.0%
# Interpretation

The verifier achieved a citation error detection accuracy of
62.5% on the pilot sample.

However, its performance decreased substantially when the task
required identifying the precise type of citation error.

The error-type accuracy was 10.0%, while exact correction accuracy
was 0.0% under the deterministic normalization used in the pilot
evaluation.

This indicates that the verifier was considerably better at the
higher-level decision of whether a citation was potentially incorrect
than at reconstructing the exact citation component expected by the
benchmark.

These results are therefore treated as a limitation of the current
verification approach rather than evidence of reliable automatic
citation correction.

# 6. CAT4.2 — Case Verification
# 6.1 Task

CAT4.2 evaluates whether a cited case is the appropriate authority
for the legal proposition described in the question.

The benchmark contains both:

Correctly cited cases (4-2-true)
Incorrectly cited cases (4-2-fake)

For incorrect cases, the benchmark provides the correct case and
citation as ground-truth information.

# 6.2 Pilot Configuration

A balanced pilot sample of 40 CAT4.2 records was evaluated:

| Category  | Number of records |
| --------- | ----------------: |
| 4-2-true  |                20 |
| 4-2-fake  |                20 |
| **Total** |            **40** |

The pilot predictions are preserved in:

results/stage2/cat4_2_pilot_predictions.jsonl

The evaluated results are preserved in:

results/stage2/cat4_2_results.csv

# 6.3 CAT4.2 Results
| Metric                         |    Result |
| ------------------------------ | --------: |
| Case verification accuracy     | **92.5%** |
| Case-name exact-match accuracy | **17.5%** |
| Citation exact-match accuracy  | **45.0%** |

# Interpretation
The verifier achieved 92.5% case verification accuracy on the
40-record pilot.

The substantially lower case-name and citation exact-match values
should be interpreted cautiously.

Legal case names frequently contain differences in whitespace,
punctuation, capitalization, party-role labels, and formatting.
Similarly, citation strings may differ in harmless formatting such
as inclusion of the decision year.

Consequently, exact string matching is a stricter criterion than
semantic case identification.

The case-verification accuracy is therefore treated as the primary
CAT4.2 pilot metric, while exact case-name and citation matching are
reported as supplementary measurements.

# 7. Overall Stage 2 Results
| Benchmark Category              | Records | Primary Metric        |    Result |
| ------------------------------- | ------: | --------------------- | --------: |
| CAT3 — Citation Error Detection |      40 | Detection Accuracy    | **62.5%** |
| CAT3 — Citation Error Detection |      40 | Error-Type Accuracy   | **10.0%** |
| CAT3 — Citation Error Detection |      40 | Correction Accuracy   |  **0.0%** |
| CAT4.2 — Case Verification      |      40 | Verification Accuracy | **92.5%** |
| CAT4.2 — Case Verification      |      40 | Case-Name Exact Match | **17.5%** |
| CAT4.2 — Case Verification      |      40 | Citation Exact Match  | **45.0%** |

# 8. Prediction and Evaluation Procedure

The evaluation follows two independent phases.

Phase 1 — Prediction

Each benchmark record is supplied to the verification model.

The model does not receive the gold annotation.

The resulting prediction is immediately stored in JSONL format.

This produces:

cat3_pilot_predictions.jsonl
cat4_2_pilot_predictions.jsonl
Phase 2 — Deterministic Evaluation

The saved predictions are compared against the benchmark annotations
using a deterministic Python evaluation script.

The evaluator is:

scripts/evaluate_stage2_pilot.py

The evaluator produces:

cat3_results.csv
cat4_2_results.csv
stage2_summary.json

This separation ensures that the gold annotations are used for
evaluation rather than prediction.

# 9. Reproducibility

The Stage 2 pipeline can be reproduced using the following scripts.

Dataset inspection
scripts/test_legalcitebench.py
Model/verifier test
scripts/test_groq_verifier.py
CAT3 diagnostic test
scripts/test_cat3_failed_cases.py
Pilot prediction generation
scripts/run_stage2_pilot.py
Deterministic evaluation
scripts/evaluate_stage2_pilot.py

The complete Stage 2 implementation is located under:

src/verification/
# 10. Stored Experimental Artifacts

The following artifacts are preserved for reproducibility and
inspection:

results/stage2/

├── cat3_pilot_predictions.jsonl

├── cat3_results.csv

├── cat4_2_pilot_predictions.jsonl

├── cat4_2_results.csv

└── stage2_summary.json

The JSONL prediction files preserve the individual model outputs,
while the CSV files contain the corresponding deterministic
evaluation results.

The JSON summary contains the aggregate pilot metrics.

# 11. Limitations

The Stage 2 experiment is a pilot evaluation, not a full
LegalCiteBench benchmark evaluation.

The pilot sample contains 40 records for CAT3 and 40 records for
CAT4.2.

The CAT3 results demonstrate a limitation in precise citation-error
classification and correction. Although the verifier can identify
citation validity with moderate performance, it performs poorly when
required to determine the exact corrupted citation component and
reconstruct the benchmark's expected correction.

CAT4.2 produced substantially stronger case-verification performance.
However, exact case-name and citation matching is sensitive to
formatting differences and should therefore not be interpreted as
equivalent to semantic case verification.

Stage 2 does not establish the correctness of complete generated
Legal RAG answers. It evaluates the verification component
independently.

# 12. Role of Stage 2 in the Overall Research Pipeline

Stage 2 follows the retrieval evaluation performed in Stage 1.

The two stages address different components:

Stage 1
Retrieval Evaluation
        |
        v
Can relevant legal evidence
be retrieved?
        |
        v
Stage 2
Legal Citation Verification
        |
        v
Can legal citations and
case authorities be verified?
        |
        v
Stage 3
End-to-End Legal RAG +
Hallucination Detection +
Adaptive Mitigation

Stage 2 therefore provides an independent benchmark-based evaluation
of the verification component before it is incorporated into the
complete Legal RAG and adaptive hallucination-mitigation pipeline.

# 13. Stage 2 Status

Status: Completed — Pilot Evaluation

The Stage 2 pilot has established a reproducible evaluation pipeline
using LegalCiteBench CAT3 and CAT4.2.

The results and raw predictions are preserved in the repository for
subsequent analysis and reporting.

The next stage evaluates the complete Legal RAG pipeline and the
proposed adaptive hallucination-mitigation mechanism.
