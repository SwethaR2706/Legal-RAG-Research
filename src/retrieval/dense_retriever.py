from sentence_transformers import SentenceTransformer 
import numpy as np 
from pathlib import Path 

from src .config import hf_config 

class DenseRetriever :

    def __init__ (
    self ,
    model_name ="BAAI/bge-m3",
    cache_name ="dense_embeddings.npy"
    ):

        print (
        f"Loading embedding model: {model_name }"
        )

        self .model =SentenceTransformer (
        model_name 
        )

        self .corpus =None 
        self .embeddings =None 

        self .cache_dir =(
        Path (__file__ ).resolve ().parents [2 ]
        /"data"
        /"indexes"
        )

        self .cache_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )

        self .cache_name =cache_name 

    def build_index (
    self ,
    corpus ,
    use_cache =True 
    ):

        if not corpus :
            raise ValueError (
            "Corpus is empty."
            )

        self .corpus =corpus 

        texts =[
        item ["text"]
        for item in corpus 
        ]

        cache_path =(
        self .cache_dir 
        /self .cache_name 
        )

        if use_cache and cache_path .exists ():

            cached =np .load (
            cache_path 
            )

            if (
            cached .shape [0 ]
            ==len (corpus )
            ):

                self .embeddings =cached 

                print (
                f"✓ Loaded cached dense embeddings "
                f"from {cache_path }"
                )

                return 

            print (
            "⚠ Cached embeddings do not match "
            "current corpus. Rebuilding..."
            )

        print (
        f"Encoding {len (texts )} documents "
        f"with batch_size=1..."
        )

        self .embeddings =self .model .encode (
        texts ,
        batch_size =1 ,
        normalize_embeddings =True ,
        show_progress_bar =True ,
        convert_to_numpy =True 
        )

        self .embeddings =np .asarray (
        self .embeddings 
        )

        np .save (
        cache_path ,
        self .embeddings 
        )

        print (
        f"✓ Dense index built"
        )

        print (
        f"✓ Embeddings saved to "
        f"{cache_path }"
        )


    def search (
    self ,
    query ,
    top_k =10 
    ):

        if self .embeddings is None :

            raise RuntimeError (
            "Dense index has not been built."
            )

        query_embedding =self .model .encode (
        query ,
        normalize_embeddings =True ,
        convert_to_numpy =True 
        )

        scores =(
        self .embeddings 
        @query_embedding 
        )

        top_indices =np .argsort (
        scores 
        )[::-1 ][:top_k ]

        results =[]

        for rank ,index in enumerate (
        top_indices ,
        start =1 
        ):

            item =self .corpus [index ]

            result =item .copy ()

            result ["id"]=item ["id"]

            result ["chunk_id"]=item ["id"]

            result ["dense_score"]=float (
            scores [index ]
            )

            result ["dense_rank"]=rank 

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
        print ("DENSE RETRIEVAL RESULTS")
        print ("="*60 )

        for i ,result in enumerate (
        results ,
        start =1 
        ):

            print (
            f"{i }. "
            f"{result ['id']} | "
            f"Score: "
            f"{result ['dense_score']:.4f}"
            )

            print (
            result ["text"][:200 ]
            )

            print ("-"*60 )