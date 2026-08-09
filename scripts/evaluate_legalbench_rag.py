from src .datasets .legalbench_rag_loader import LegalBenchRAGLoader 

from src .retrieval .dense_retriever import DenseRetriever 
from src .retrieval .sparse_retriever import SparseRetriever 
from src .retrieval .hybrid_retriever import HybridRetriever 


K_VALUES =[5 ,10 ,20 ]

def precision_at_k (
retrieved ,
gold ,
k 
):

    retrieved =retrieved [:k ]

    if not retrieved :
        return 0.0 

    hits =sum (
    1 
    for item in retrieved 
    if item ["id"]in gold 
    )

    return hits /k 

def recall_at_k (
retrieved ,
gold ,
k 
):

    if not gold :
        return 0.0 

    retrieved =retrieved [:k ]

    hits =sum (
    1 
    for item in retrieved 
    if item ["id"]in gold 
    )

    return hits /len (gold )

def f1 (
precision ,
recall 
):

    if precision +recall ==0 :
        return 0.0 

    return (
    2 *precision *recall 
    /(precision +recall )
    )

def reciprocal_rank (
retrieved ,
gold 
):

    for rank ,item in enumerate (
    retrieved ,
    start =1 
    ):

        if item ["id"]in gold :

            return 1.0 /rank 

    return 0.0 

def average_precision (
retrieved ,
gold 
):

    if not gold :
        return 0.0 

    hits =0 
    precision_sum =0.0 

    for rank ,item in enumerate (
    retrieved ,
    start =1 
    ):

        if item ["id"]in gold :

            hits +=1 

            precision_sum +=(
            hits /rank 
            )

    return precision_sum /len (gold )

def bpref (
retrieved ,
gold 
):

    if not gold :
        return 0.0 

    relevant_count =len (gold )

    non_relevant_seen =0 
    score_sum =0.0 

    relevant_found =0 

    for item in retrieved :

        item_id =item ["id"]

        if item_id in gold :

            score_sum +=(
            1 
            -min (
            non_relevant_seen ,
            relevant_count 
            )
            /relevant_count 
            )

            relevant_found +=1 

            if relevant_found ==relevant_count :
                break 

        else :

            non_relevant_seen +=1 

    return score_sum /relevant_count 

def evaluate_method (
predictions ,
gold_by_query 
):

    results ={}

    for k in K_VALUES :

        precisions =[]
        recalls =[]
        f1_scores =[]

        for query_id ,retrieved in predictions .items ():

            gold =gold_by_query [query_id ]

            p =precision_at_k (
            retrieved ,
            gold ,
            k 
            )

            r =recall_at_k (
            retrieved ,
            gold ,
            k 
            )

            precisions .append (p )
            recalls .append (r )

            f1_scores .append (
            f1 (p ,r )
            )

        results [k ]={

        "precision":
        sum (precisions )
        /len (precisions ),

        "recall":
        sum (recalls )
        /len (recalls ),

        "f1":
        sum (f1_scores )
        /len (f1_scores )

        }

    rr_scores =[]

    for query_id ,retrieved in predictions .items ():

        rr_scores .append (
        reciprocal_rank (
        retrieved ,
        gold_by_query [query_id ]
        )
        )

    results ["mrr"]=(
    sum (rr_scores )
    /len (rr_scores )
    )

    ap_scores =[]

    for query_id ,retrieved in predictions .items ():

        ap_scores .append (
        average_precision (
        retrieved ,
        gold_by_query [query_id ]
        )
        )

    results ["map"]=(
    sum (ap_scores )
    /len (ap_scores )
    )

    bpref_scores =[]

    for query_id ,retrieved in predictions .items ():

        bpref_scores .append (
        bpref (
        retrieved ,
        gold_by_query [query_id ]
        )
        )

    results ["bpref"]=(
    sum (bpref_scores )
    /len (bpref_scores )
    )

    return results 

def print_results (
name ,
results 
):

    print ()
    print ("="*60 )
    print (name )
    print ("="*60 )

    for k in K_VALUES :

        r =results [k ]

        print (
        f"@{k }"
        )

        print (
        f"Precision : "
        f"{r ['precision']:.4f}"
        )

        print (
        f"Recall    : "
        f"{r ['recall']:.4f}"
        )

        print (
        f"F1        : "
        f"{r ['f1']:.4f}"
        )

    print (
    f"\nMAP       : "
    f"{results ['map']:.4f}"
    )

    print (
    f"BPREF     : "
    f"{results ['bpref']:.4f}"
    )

    print (
    f"MRR       : "
    f"{results ['mrr']:.4f}"
    )

def main ():

    print ("="*60 )
    print ("LEGALBENCH-RAG STAGE 1 EVALUATION")
    print ("="*60 )

    loader =LegalBenchRAGLoader ()

    data =loader .load ()

    corpus =data ["corpus"]
    queries =data ["queries"]

    print (
    f"\nCorpus  : {len (corpus )}"
    )

    print (
    f"Queries : {len (queries )}"
    )

    gold_by_query ={

    query ["id"]:
    set (query ["relevant_ids"])

    for query in queries 

    }

    print (
    "\nBuilding dense retriever..."
    )

    dense =DenseRetriever (
    cache_name ="legalbench_rag_bge_m3.npy"
    )

    dense .build_index (
    corpus 
    )





    print (
    "\nBuilding sparse retriever..."
    )

    sparse =SparseRetriever ()

    sparse .build_index (
    corpus 
    )





    print (
    "\nBuilding hybrid retriever..."
    )

    hybrid =HybridRetriever (
    dense =dense ,
    sparse =sparse 
    )

    hybrid .corpus =corpus 





    dense_predictions ={}

    sparse_predictions ={}

    rrf_predictions ={}

    score_fusion_predictions ={}





    for index ,query in enumerate (
    queries ,
    start =1 
    ):

        query_id =query ["id"]

        text =query ["query"]

        print (
        f"\n[{index }/{len (queries )}] "
        f"{query_id }"
        )





        dense_results =dense .search (
        text ,
        top_k =100 
        )

        dense_predictions [
        query_id 
        ]=dense_results 





        sparse_results =sparse .search (
        text ,
        top_k =100 
        )

        sparse_predictions [
        query_id 
        ]=sparse_results 





        rrf_results =hybrid .search (
        text ,
        candidate_k =100 ,
        top_k =100 
        )

        rrf_predictions [
        query_id 
        ]=rrf_results 





        score_fusion_results =(
        hybrid .search_score_fusion (
        text ,
        candidate_k =100 ,
        top_k =100 
        )
        )

        score_fusion_predictions [
        query_id 
        ]=score_fusion_results 





    print (
    "\n\n"
    +"="*60 
    )

    print (
    "CALCULATING FINAL METRICS"
    )

    print (
    "="*60 
    )

    dense_metrics =evaluate_method (
    dense_predictions ,
    gold_by_query 
    )

    sparse_metrics =evaluate_method (
    sparse_predictions ,
    gold_by_query 
    )

    rrf_metrics =evaluate_method (
    rrf_predictions ,
    gold_by_query 
    )

    score_fusion_metrics =evaluate_method (
    score_fusion_predictions ,
    gold_by_query 
    )





    print_results (
    "DENSE BGE-M3",
    dense_metrics 
    )

    print_results (
    "SPARSE BM25",
    sparse_metrics 
    )

    print_results (
    "HYBRID RRF",
    rrf_metrics 
    )

    print_results (
    "HYBRID SCORE FUSION",
    score_fusion_metrics 
    )





    print (
    "\n"
    +"="*60 
    )

    print (
    "STAGE 1B SUMMARY"
    )

    print (
    "="*60 
    )

    print (
    "\nLegalBench-RAG evaluation completed."
    )

    print (
    "Methods evaluated:"
    )

    print (
    "1. BGE-M3"
    )

    print (
    "2. BM25"
    )

    print (
    "3. Hybrid RRF"
    )

    print (
    "4. Hybrid Score Fusion"
    )

    print (
    "\nMetrics:"
    )

    print (
    "Precision@5, @10, @20"
    )

    print (
    "Recall@5, @10, @20"
    )

    print (
    "F1@5, @10, @20"
    )

    print (
    "MAP"
    )

    print (
    "BPREF"
    )

    print (
    "MRR"
    )


if __name__ =="__main__":

    main ()