from src .retrieval .dense_retriever import DenseRetriever 
from src .retrieval .sparse_retriever import SparseRetriever 
from src .retrieval .rrf import ReciprocalRankFusion 
from src .retrieval .score_fusion import ScoreFusion 


class HybridRetriever :

    def __init__ (
    self ,
    dense =None ,
    sparse =None ,
    rrf =None ,
    score_fusion =None 
    ):

        self .dense =(
        dense 
        if dense is not None 
        else DenseRetriever ()
        )

        self .sparse =(
        sparse 
        if sparse is not None 
        else SparseRetriever ()
        )

        self .rrf =(
        rrf 
        if rrf is not None 
        else ReciprocalRankFusion (
        k =60 
        )
        )

        self .score_fusion =(
        score_fusion 
        if score_fusion is not None 
        else ScoreFusion (
        dense_weight =0.7 ,
        sparse_weight =0.3 
        )
        )

        self .corpus =None 

    def build_index (
    self ,
    corpus 
    ):

        self .corpus =corpus 

        print (
        "\nBuilding dense index..."
        )

        self .dense .build_index (
        corpus 
        )

        print (
        "\nBuilding sparse index..."
        )

        self .sparse .build_index (
        corpus 
        )

        print (
        "\n✓ Hybrid retrieval index ready"
        )

    def search (
    self ,
    query ,
    candidate_k =20 ,
    top_k =10 
    ):

        dense_results =(
        self .dense .search (
        query ,
        top_k =candidate_k 
        )
        )

        sparse_results =(
        self .sparse .search (
        query ,
        top_k =candidate_k 
        )
        )

        fused_results =self .rrf .fuse (
        dense_results ,
        sparse_results 
        )

        return fused_results [:top_k ]

    def search_score_fusion (
    self ,
    query ,
    candidate_k =100 ,
    top_k =20 
    ):

        dense_results =(
        self .dense .search (
        query ,
        top_k =candidate_k 
        )
        )

        sparse_results =(
        self .sparse .search (
        query ,
        top_k =candidate_k 
        )
        )

        fused_results =(
        self .score_fusion .fuse (
        dense_results ,
        sparse_results 
        )
        )

        return fused_results [:top_k ]

    def search_union (
    self ,
    query ,
    candidate_k =100 
    ):

        dense_results =(
        self .dense .search (
        query ,
        top_k =candidate_k 
        )
        )

        sparse_results =(
        self .sparse .search (
        query ,
        top_k =candidate_k 
        )
        )

        candidates ={}


        for item in dense_results :

            candidates [
            item ["id"]
            ]=item .copy ()


        for item in sparse_results :

            item_id =item ["id"]

            if item_id not in candidates :

                candidates [
                item_id 
                ]=item .copy ()

        return list (
        candidates .values ()
        )

    def display (
    self ,
    results 
    ):

        print ()
        print ("="*60 )
        print ("HYBRID RESULTS")
        print ("="*60 )

        for i ,item in enumerate (
        results ,
        start =1 
        ):

            if "rrf_score"in item :

                score_text =(
                f"RRF: "
                f"{item ['rrf_score']:.6f}"
                )

            elif "hybrid_score"in item :

                score_text =(
                f"Hybrid: "
                f"{item ['hybrid_score']:.6f}"
                )

            else :

                score_text =""

            print (
            f"{i }. "
            f"{item ['id']} | "
            f"{score_text }"
            )

            print (
            item ["text"][:200 ]
            )

            print (
            "-"*60 
            )