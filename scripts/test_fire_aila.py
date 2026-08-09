from src .datasets .fire_aila_loader import FIREAILALoader 
from src .retrieval .hybrid_retriever import HybridRetriever 


def main ():

    print ("="*60 )
    print ("FIRE AILA RETRIEVAL TEST")
    print ("="*60 )

    loader =FIREAILALoader ()

    data =loader .load ()

    statutes =data ["statutes"]
    queries =data ["queries"]

    print (
    f"\nStatutes : {len (statutes )}"
    )

    print (
    f"Queries  : {len (queries )}"
    )

    corpus =[]

    for statute in statutes :

        corpus .append ({

        "id":statute ["id"],

        "title":statute ["title"],

        "text":statute ["text"]

        })

    hybrid =HybridRetriever ()

    hybrid .build_index (
    corpus 
    )

    query =queries [0 ]

    print (
    "\n"+"="*60 
    )

    print (
    f"QUERY: {query ['id']}"
    )

    print (
    "="*60 
    )

    print (
    query ["query"]
    )

    gold =set (
    query ["relevant_ids"]
    )

    print (
    "\nGold statutes:"
    )

    print (
    sorted (gold )
    )

    rrf_results =hybrid .search (
    query ["query"],
    candidate_k =20 ,
    top_k =20 
    )

    print (
    "\n"+"="*60 
    )

    print (
    "RRF RESULTS"
    )

    print (
    "="*60 
    )

    for i ,item in enumerate (
    rrf_results ,
    start =1 
    ):

        marker =(
        " ✓ GOLD"
        if item ["id"]in gold 
        else ""
        )

        print (
        f"{i }. "
        f"{item ['id']} | "
        f"RRF: "
        f"{item ['rrf_score']:.6f}"
        f"{marker }"
        )

    score_results =hybrid .search_score_fusion (
    query ["query"],
    candidate_k =100 ,
    top_k =20 
    )

    print (
    "\n"+"="*60 
    )

    print (
    "SCORE FUSION RESULTS"
    )

    print (
    "="*60 
    )

    for i ,item in enumerate (
    score_results ,
    start =1 
    ):

        marker =(
        " ✓ GOLD"
        if item ["id"]in gold 
        else ""
        )

        print (
        f"{i }. "
        f"{item ['id']} | "
        f"Hybrid: "
        f"{item ['hybrid_score']:.6f}"
        f"{marker }"
        )

    union_candidates =hybrid .search_union (
    query ["query"],
    candidate_k =100 
    )

    union_gold =[
    item ["id"]
    for item in union_candidates 
    if item ["id"]in gold 
    ]

    print (
    "\n"+"="*60 
    )

    print (
    "DENSE + SPARSE UNION"
    )

    print (
    "="*60 
    )

    print (
    f"Candidates: "
    f"{len (union_candidates )}"
    )

    print (
    f"Gold found: "
    f"{union_gold }"
    )

    print (
    f"Candidate recall: "
    f"{len (union_gold )}/{len (gold )}"
    )

if __name__ =="__main__":
    main ()