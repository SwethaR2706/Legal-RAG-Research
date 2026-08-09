from src .datasets .il_tur_corpus import ILTURCorpus 

from src .retrieval .hybrid_retriever import (
HybridRetriever 
)

from src .reranking .cross_encoder import (
CrossEncoderReranker 
)

def main ():

    builder =ILTURCorpus ()
    corpus =builder .build ()
    hybrid =HybridRetriever ()

    hybrid .build_index (
    corpus 
    )

    reranker =CrossEncoderReranker ()
    query =(
    "What punishment is provided for murder?"
    )

    candidates =hybrid .search (
    query ,
    candidate_k =20 ,
    top_k =20 
    )

    print (
    f"\nHybrid candidates: "
    f"{len (candidates )}"
    )

    reranked =reranker .rerank (
    query ,
    candidates ,
    top_k =5 
    )

    reranker .display (
    reranked 
    )


if __name__ =="__main__":

    main ()