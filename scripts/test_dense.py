from src .datasets .il_tur_corpus import ILTURCorpus 
from src .retrieval .dense_retriever import DenseRetriever 

from src .config import hf_config 
def main ():

    builder =ILTURCorpus ()

    corpus =builder .build ()

    retriever =DenseRetriever ()

    retriever .build_index (
    corpus 
    )

    query =(
    "When does culpable homicide become murder?"
    )

    results =retriever .search (
    query ,
    top_k =5 
    )

    retriever .display (
    results 
    )


if __name__ =="__main__":

    main ()