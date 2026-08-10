import argparse 
import json 
from pathlib import Path 

from src .datasets .il_tur_lsi_loader import ILTURLSILoader 
from src .retrieval .hybrid_retriever import HybridRetriever 
from src .reranking .cross_encoder import CrossEncoderReranker 

def calculate_metrics (predicted ,gold ):
    predicted =set (predicted )
    gold =set (gold )

    true_positive =len (
    predicted .intersection (gold )
    )

    precision =(
    true_positive /len (predicted )
    if predicted 
    else 0.0 
    )

    recall =(
    true_positive /len (gold )
    if gold 
    else 0.0 
    )

    if precision +recall ==0 :
        f1 =0.0 
    else :
        f1 =(
        2 *precision *recall 
        /(precision +recall )
        )

    return precision ,recall ,f1 


def evaluate_at_k (predictions ,k ):
    precision_sum =0.0 
    recall_sum =0.0 
    f1_sum =0.0 

    for item in predictions :

        predicted =item ["predicted"][:k ]
        gold =item ["gold"]

        precision ,recall ,f1 =calculate_metrics (
        predicted ,
        gold 
        )

        precision_sum +=precision 
        recall_sum +=recall 
        f1_sum +=f1 

    n =len (predictions )

    return {
    "precision":precision_sum /n ,
    "recall":recall_sum /n ,
    "f1":f1_sum /n 
    }


def evaluate_recall_at_k (predictions ,k ):
    recall_sum =0.0 

    for item in predictions :

        predicted =set (
        item ["predicted"][:k ]
        )

        gold =set (
        item ["gold"]
        )

        recall =(
        len (predicted .intersection (gold ))
        /len (gold )
        if gold 
        else 0.0 
        )

        recall_sum +=recall 

    return recall_sum /len (predictions )


def main ():

    parser =argparse .ArgumentParser ()

    parser .add_argument (
    "--limit",
    type =int ,
    default =100 
    )

    parser .add_argument (
    "--candidate-k",
    type =int ,
    default =100 
    )

    args =parser .parse_args ()

    loader =ILTURLSILoader ()

    dataset =loader .load ()

    cases =dataset ["cases"]
    statutes =dataset ["statutes"]

    if args .limit >0 :
        cases =cases [:args .limit ]

    print ("="*70 )
    print ("IL-TUR LSI EVALUATION")
    print ("="*70 )

    print (
    f"Cases       : {len (cases )}"
    )

    print (
    f"Statutes    : {len (statutes )}"
    )

    print (
    f"Candidate K : {args .candidate_k }"
    )

    corpus =[
    {
    "id":statute ["id"],
    "text":statute ["text"]
    }
    for statute in statutes 
    ]

    hybrid =HybridRetriever ()

    hybrid .build_index (
    corpus 
    )

    reranker =CrossEncoderReranker ()

    hybrid_predictions =[]
    reranked_predictions =[]
    
    for index ,case in enumerate (
    cases ,
    start =1 
    ):

        query =case ["query"]

        gold =case ["gold_statutes"]

        hybrid_results =hybrid .search (
        query ,
        candidate_k =args .candidate_k ,
        top_k =args .candidate_k 
        )

        hybrid_ids =[
        item ["id"]
        for item in hybrid_results 
        ]

        hybrid_predictions .append ({
        "id":case ["id"],
        "gold":gold ,
        "predicted":hybrid_ids 
        })

        reranked =reranker .rerank (
        query ,
        hybrid_results ,
        top_k =args .candidate_k 
        )

        reranked_ids =[
        item ["id"]
        for item in reranked 
        ]

        reranked_predictions .append ({
        "id":case ["id"],
        "gold":gold ,
        "predicted":reranked_ids 
        })

        if index %10 ==0 :

            print (
            f"Processed "
            f"{index }/{len (cases )}"
            )

    k_values =[
    10 ,
    20 ,
    50 ,
    100 
    ]

    print ()
    print ("="*70 )
    print ("HYBRID RRF RESULTS")
    print ("="*70 )

    for k in k_values :

        metrics =evaluate_at_k (
        hybrid_predictions ,
        k 
        )

        print (
        f"\n@{k }"
        )

        print (
        f"Precision : "
        f"{metrics ['precision']:.4f}"
        )

        print (
        f"Recall    : "
        f"{metrics ['recall']:.4f}"
        )

        print (
        f"F1        : "
        f"{metrics ['f1']:.4f}"
        )

    print ()
    print ("="*70 )
    print ("CROSS-ENCODER RESULTS")
    print ("="*70 )

    for k in k_values :

        metrics =evaluate_at_k (
        reranked_predictions ,
        k 
        )

        print (
        f"\n@{k }"
        )

        print (
        f"Precision : "
        f"{metrics ['precision']:.4f}"
        )

        print (
        f"Recall    : "
        f"{metrics ['recall']:.4f}"
        )

        print (
        f"F1        : "
        f"{metrics ['f1']:.4f}"
        )

    print ()
    print ("="*70 )
    print ("CANDIDATE RECALL")
    print ("="*70 )

    for k in k_values :

        hybrid_recall =evaluate_recall_at_k (
        hybrid_predictions ,
        k 
        )

        reranked_recall =evaluate_recall_at_k (
        reranked_predictions ,
        k 
        )

        print (
        f"\n@{k }"
        )

        print (
        f"Hybrid RRF      : "
        f"{hybrid_recall :.4f}"
        )

        print (
        f"Cross-Encoder   : "
        f"{reranked_recall :.4f}"
        )

    output_dir =(
    Path ("results")
    /"il_tur"
    )

    output_dir .mkdir (
    parents =True ,
    exist_ok =True 
    )

    with open (
    output_dir /"hybrid_predictions.json",
    "w",
    encoding ="utf-8"
    )as f :

        json .dump (
        hybrid_predictions ,
        f ,
        indent =2 ,
        ensure_ascii =False 
        )

    with open (
    output_dir /"reranked_predictions.json",
    "w",
    encoding ="utf-8"
    )as f :

        json .dump (
        reranked_predictions ,
        f ,
        indent =2 ,
        ensure_ascii =False 
        )

    print ()
    print (
    "✓ Predictions saved to "
    "results/il_tur/"
    )

if __name__ =="__main__":
    main ()