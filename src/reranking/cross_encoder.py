from sentence_transformers import CrossEncoder 

from src .config import hf_config 


class CrossEncoderReranker :

    def __init__ (
    self ,
    model_name ="jinaai/jina-reranker-v2-base-multilingual"
    ):

        self .model_name =model_name 

        print (
        f"Loading Cross Encoder: "
        f"{self .model_name }"
        )

        self .model =CrossEncoder (
        self .model_name ,
        max_length =1024 ,
        trust_remote_code =True 
        )

    def rerank (
    self ,
    query ,
    candidates ,
    top_k =10 
    ):

        if not candidates :
            return []

        pairs =[]

        for item in candidates :

            title =item .get (
            "title",
            item .get (
            "section_title",
            ""
            )
            )

            passage =(
            f"Title: {title }\n\n"
            f"{item ['text']}"
            )

            pairs .append (
            (
            query ,
            passage 
            )
            )

        scores =self .model .predict (
        pairs ,
        show_progress_bar =True 
        )

        reranked =[]

        for item ,score in zip (
        candidates ,
        scores 
        ):

            result =item .copy ()

            result ["cross_score"]=float (
            score 
            )

            reranked .append (
            result 
            )

        reranked .sort (
        key =lambda x :x ["cross_score"],
        reverse =True 
        )

        return reranked [:top_k ]

    def display (
    self ,
    results 
    ):

        print ()
        print ("="*60 )
        print ("CROSS-ENCODER RESULTS")
        print ("="*60 )

        for i ,item in enumerate (
        results ,
        start =1 
        ):

            print (
            f"{i }. "
            f"{item ['id']} | "
            f"Cross: "
            f"{item ['cross_score']:.6f}"
            )

            if item .get ("title"):

                print (
                f"Title: {item ['title']}"
                )

            print (
            item ["text"][:200 ]
            )

            print (
            "-"*60 
            )