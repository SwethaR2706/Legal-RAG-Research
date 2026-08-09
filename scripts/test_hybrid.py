from src .datasets .il_tur_corpus import ILTURCorpus 
from src .retrieval .hybrid_retriever import HybridRetriever 

def main ():

    builder =ILTURCorpus ()

    corpus =builder .build ()

    retriever =HybridRetriever ()

    retriever .build_index (
    corpus 
    )

    query =(
    "What punishment is provided for murder?"
    )

    results =retriever .search (
    query ,
    candidate_k =20 ,
    top_k =5 
    )

    retriever .display (
    results 
    )

if __name__ =="__main__":

    main ()