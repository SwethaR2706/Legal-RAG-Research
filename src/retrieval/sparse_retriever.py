from rank_bm25 import BM25Okapi 
import re 

class SparseRetriever :

    def __init__ (self ):

        self .corpus =None 
        self .tokenized_corpus =None 
        self .bm25 =None 

    def build_index (
    self ,
    corpus 
    ):

        if not corpus :
            raise ValueError (
            "Corpus is empty."
            )

        self .corpus =corpus 

        self .tokenized_corpus =[

        self .tokenize (
        item ["text"]
        )

        for item in corpus 

        ]

        self .bm25 =BM25Okapi (
        self .tokenized_corpus 
        )

        print (
        f"✓ BM25 index built for "
        f"{len (corpus )} documents"
        )

    def tokenize (
    self ,
    text 
    ):

        return re .findall (
        r"\b\w+\b",
        text .lower ()
        )

    def search (
    self ,
    query ,
    top_k =10 
    ):

        if self .bm25 is None :

            raise RuntimeError (
            "BM25 index has not been built."
            )

        query_tokens =self .tokenize (
        query 
        )

        scores =self .bm25 .get_scores (
        query_tokens 
        )

        ranked_indices =sorted (
        range (len (scores )),
        key =lambda i :scores [i ],
        reverse =True 
        )[:top_k ]

        results =[]

        for rank ,index in enumerate (
        ranked_indices ,
        start =1 
        ):

            item =self .corpus [index ]

            result =item .copy ()

            result ["id"]=item ["id"]



            result ["chunk_id"]=item ["id"]

            result ["sparse_score"]=float (
            scores [index ]
            )

            result ["sparse_rank"]=rank 

            results .append (
            result 
            )

        return results 

    def display (
    self ,
    results 
    ):

        print ()
        print ("="*60 )
        print ("BM25 SPARSE RETRIEVAL RESULTS")
        print ("="*60 )

        for i ,result in enumerate (
        results ,
        start =1 
        ):

            print (
            f"{i }. "
            f"{result ['id']} | "
            f"Score: "
            f"{result ['sparse_score']:.4f}"
            )

            print (
            result ["text"][:200 ]
            )

            print ("-"*60 )