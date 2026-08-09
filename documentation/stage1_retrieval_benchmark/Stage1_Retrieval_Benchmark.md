# Stage 1 - Retrieval Benchmarking

## 1. Objective
The objective of Stage 1 was to empirically evaluate alternative retrieval strategies for the Legal RAG pipeline and identify a suitable retrieval configuration for subsequent stages.
## 2. Research Question
RQ1: Which retrieval strategy provides the strongest retrieval performance for legal information retrieval among dense, sparse, and hybrid approaches?
## 3. Experimental Setup
FIRE AILA
| Property         |                       Value |
| ---------------- | --------------------------: |
| Dataset          |              FIRE AILA 2019 |
| Corpus           |                197 statutes |
| Queries          |                          50 |
| Retrieval target |                 Statute IDs |
| Relevance source | Dataset relevance judgments |

LegalBench-RAG
| Property         |                 Value |
| ---------------- | --------------------: |
| Dataset          |        LegalBench-RAG |
| Corpus           |        4,876 passages |
| Queries          |                   100 |
| Retrieval target |           Passage IDs |
| Relevance source | `relevant_passage_id` |


### 3.1 FIRE AILA
The FIRE AILA benchmark contains legal situation-based queries and relevance judgments identifying statutes relevant to each query. The 197 statutes were used as the retrieval corpus and the 50 queries were evaluated against their corresponding relevance judgments.
### 3.2 LegalBench-RAG
LegalBench-RAG was used as a second retrieval benchmark. The corpus contains 4,876 passages and the evaluation set contains 100 questions, each associated with a relevant passage identifier.
## 4. Retrieval Methods
Stage 1 evaluates four retrieval configurations under a common experimental protocol:

BGE-M3 Dense Retrieval
BM25 Sparse Retrieval
Hybrid Retrieval using Reciprocal Rank Fusion (RRF)
Hybrid Retrieval using Score Fusion

The same query sets, corpora, relevance judgments, candidate depth, and evaluation metrics were used when comparing the retrieval methods.
### 4.1 BGE-M3
Dense retrieval was implemented using BAAI/bge-m3.

Each corpus passage/statute was converted into a normalized embedding. Queries were encoded using the same model, and documents were ranked using embedding similarity.

The resulting dense embeddings were cached to avoid recomputing them during repeated evaluations.

Purpose: Capture semantic similarity between legal queries and legal documents, even when they use different wording.
### 4.2 BM25
Sparse retrieval was implemented using BM25 through the rank_bm25 library.

The corpus was tokenized and indexed using BM25. Each query was tokenized using the same procedure, and documents were ranked according to their BM25 relevance scores.

Purpose: Capture exact and lexical relationships between query terms and legal documents.
### 4.3 Hybrid RRF
Hybrid RRF combines the rankings produced by BGE-M3 and BM25 using Reciprocal Rank Fusion (RRF).

Instead of directly combining the scores from the two retrievers, RRF combines their ranking positions to produce a unified ranking.

Purpose: Combine semantic retrieval from BGE-M3 with lexical retrieval from BM25.
### 4.4 Hybrid Score Fusion
Hybrid Score Fusion combines the normalized retrieval scores from BGE-M3 and BM25.

The dense and sparse retrieval signals are normalized and combined into a single hybrid score, after which documents are ranked according to the resulting score.

Purpose: Determine whether directly combining dense and sparse relevance signals provides better retrieval performance than either method independently or RRF.
## 5. Evaluation Metrics
Stage 1 evaluates retrieval performance at @5, @10, and @20.

The following metrics were used:

Precision
Recall
F1
MAP
BPREF
MRR
### 5.1 Precision
Measures how many of the retrieved documents are relevant.

Higher precision means fewer irrelevant documents appear in the retrieved results.
### 5.2 Recall
Measures how many of the known relevant documents were successfully retrieved.

Higher recall means more relevant documents were recovered.
### 5.3 F1
F1 combines Precision and Recall into a single measure.

It is useful for evaluating the balance between retrieving relevant documents and avoiding irrelevant results.
### 5.4 MAP
Mean Average Precision measures the overall ranking quality of relevant documents across queries.

Higher MAP indicates that relevant documents tend to appear at better positions in the ranking.
### 5.5 BPREF
BPREF measures the ordering of relevant documents relative to non-relevant documents.

Higher BPREF indicates better ranking of relevant documents.
### 5.6 MRR
Mean Reciprocal Rank measures how early the first relevant document appears in the ranking.

Higher MRR indicates that relevant results generally appear closer to the top.
## 6. FIRE AILA Results
FIRE AILA contains:

197 statutes
50 queries
Dataset-provided relevance judgments

Results
| Method                  |        P@5 |        R@5 |       F1@5 |       P@10 |       R@10 |      F1@10 |       P@20 |       R@20 |      F1@20 |        MAP |      BPREF |        MRR |
| ----------------------- | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: |
| BGE-M3                  |     0.0960 |     0.1170 |     0.1044 |     0.0740 |     0.1757 |     0.1034 |     0.0610 |     0.2767 |     0.0996 |     0.1107 |     0.0693 |     0.2690 |
| BM25                    |     0.0600 |     0.0723 |     0.0651 |     0.0540 |     0.1303 |     0.0756 |     0.0390 |     0.1863 |     0.0642 |     0.0657 |     0.0436 |     0.1946 |
| Hybrid RRF              |     0.0880 |     0.1083 |     0.0957 |     0.0620 |     0.1473 |     0.0864 |     0.0480 |     0.2243 |     0.0787 |     0.0812 |     0.0501 |     0.2112 |
| **Hybrid Score Fusion** | **0.0920** | **0.1107** | **0.0992** | **0.0800** | **0.1903** | **0.1118** | **0.0560** | **0.2593** | **0.0917** | **0.1109** | **0.0704** | **0.2812** |

Observation

Hybrid Score Fusion achieved the highest:

MAP: 0.1109
BPREF: 0.0704
MRR: 0.2812

However, its improvement over BGE-M3 on FIRE AILA was small. This indicates that hybridization does not produce a large improvement on every benchmark.
## 7. LegalBench-RAG Results
LegalBench-RAG contains:

4,876 passages
100 queries
Query-level relevant passage identifiers

Results
| Method                  |        P@5 |        R@5 |       F1@5 |       P@10 |       R@10 |      F1@10 |       P@20 |       R@20 |      F1@20 |        MAP |      BPREF |        MRR |
| ----------------------- | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: |
| BGE-M3                  |     0.0700 |     0.3500 |     0.1167 |     0.0410 |     0.4100 |     0.0745 |     0.0230 |     0.4600 |     0.0438 |     0.2345 |     0.1400 |     0.2345 |
| BM25                    |     0.0600 |     0.3000 |     0.1000 |     0.0310 |     0.3100 |     0.0564 |     0.0215 |     0.4300 |     0.0410 |     0.2174 |     0.1400 |     0.2174 |
| Hybrid RRF              |     0.0640 |     0.3200 |     0.1067 |     0.0400 |     0.4000 |     0.0727 |     0.0275 |     0.5500 |     0.0524 |     0.2475 |     0.1600 |     0.2475 |
| **Hybrid Score Fusion** | **0.0760** | **0.3800** | **0.1267** | **0.0430** | **0.4300** | **0.0782** | **0.0265** | **0.5300** | **0.0505** | **0.2754** | **0.1900** | **0.2754** |

Observation

Hybrid Score Fusion achieved the highest:

MAP: 0.2754
BPREF: 0.1900
MRR: 0.2754
Precision@5: 0.0760
Recall@5: 0.3800
F1@5: 0.1267
Precision@10: 0.0430
Recall@10: 0.4300
F1@10: 0.0782

At @20, Hybrid RRF achieved the highest recall (0.5500), while Hybrid Score Fusion achieved the highest F1 (0.0505).

Overall, Hybrid Score Fusion provided the strongest ranking performance on LegalBench-RAG.
## 8. Cross-Dataset Comparison
| Dataset        | Best Method             |        MAP |      BPREF |        MRR |
| -------------- | ----------------------- | ---------: | ---------: | ---------: |
| FIRE AILA      | **Hybrid Score Fusion** | **0.1109** | **0.0704** | **0.2812** |
| LegalBench-RAG | **Hybrid Score Fusion** | **0.2754** | **0.1900** | **0.2754** |

Observation

Hybrid Score Fusion achieved the highest MAP, BPREF, and MRR on both datasets.

However, the improvement was different across the benchmarks:

FIRE AILA: improvement over BGE-M3 was marginal.
LegalBench-RAG: improvement over BGE-M3 was more substantial.

This suggests that the effectiveness of hybrid retrieval depends on the characteristics of the legal retrieval dataset.

Stage 1 selection: Hybrid Score Fusion is retained as the retrieval strategy for the subsequent stages of the Legal RAG pipeline.
## 9. Retrieval Strategy Selection
**Selected method: Hybrid Score Fusion**

Hybrid Score Fusion was selected as the retrieval strategy for the next stages because it achieved the strongest overall ranking performance across both benchmarks.

Pipeline:

Query
  |
  +----> BGE-M3 Dense Retrieval ----+
  |                                  |
  +----> BM25 Sparse Retrieval ------+
                                     |
                                     v
                            Hybrid Score Fusion
                                     |
                                     v
                              Ranked Evidence
## 10. Stage 1 Conclusion
Stage 1 compared BGE-M3, BM25, Hybrid RRF, and Hybrid Score Fusion on FIRE AILA and LegalBench-RAG.

Hybrid Score Fusion achieved the highest MAP, BPREF, and MRR on both benchmarks.

Therefore, Hybrid Score Fusion was selected as the retrieval configuration for subsequent stages.

Stage 1 evaluates retrieval only. It does not evaluate answer generation or hallucination mitigation.
## 11. Limitations
Only two retrieval benchmarks were evaluated.
Hybrid Score Fusion did not produce a large improvement on FIRE AILA.
Retrieval metrics do not measure generated-answer correctness or hallucination.
Dense retrieval currently uses NumPy similarity rather than FAISS.
Results are benchmark-dependent and should not be treated as universally representative.
## 12. Reproducibility
Datasets

FIRE AILA: 197 statutes, 50 queries

LegalBench-RAG: 4,876 passages, 100 queries

Models / Methods
Dense: BAAI/bge-m3
Sparse: BM25
Hybrid: RRF and Score Fusion
Candidate depth: 100
Evaluation cutoffs: 5, 10, 20

Evaluation Scripts
scripts/evaluate_fire_aila.py
scripts/evaluate_legalbench_rag.py

Dense corpus embeddings are cached to avoid recomputing them during repeated evaluations.

## 13. Stage 1 Status
COMPLETED / FROZEN

Stage 1 has established the retrieval baseline for the Legal RAG pipeline.

The selected retrieval configuration will be carried forward into the next stage.

No further Stage 1 changes will be made unless an implementation or evaluation error is discovered.
