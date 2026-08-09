class ScoreFusion :

    def __init__ (
    self ,
    dense_weight =0.7 ,
    sparse_weight =0.3 
    ):
        self .dense_weight =dense_weight 
        self .sparse_weight =sparse_weight 

    def normalize (self ,scores ):

        if not scores :
            return {}

        minimum =min (scores .values ())
        maximum =max (scores .values ())

        if maximum ==minimum :
            return {
            key :1.0 
            for key in scores 
            }

        return {
        key :
        (value -minimum )
        /(maximum -minimum )
        for key ,value in scores .items ()
        }

    def fuse (
    self ,
    dense_results ,
    sparse_results 
    ):

        dense_scores ={
        item ["id"]:item ["dense_score"]
        for item in dense_results 
        }

        sparse_scores ={
        item ["id"]:item ["sparse_score"]
        for item in sparse_results 
        }

        dense_norm =self .normalize (
        dense_scores 
        )

        sparse_norm =self .normalize (
        sparse_scores 
        )

        items ={}

        for item in dense_results :
            items [item ["id"]]=item .copy ()

        for item in sparse_results :
            if item ["id"]not in items :
                items [item ["id"]]=item .copy ()

        fused =[]

        for item_id ,item in items .items ():

            dense_score =dense_norm .get (
            item_id ,
            0.0 
            )

            sparse_score =sparse_norm .get (
            item_id ,
            0.0 
            )

            hybrid_score =(
            self .dense_weight *dense_score 
            +
            self .sparse_weight *sparse_score 
            )

            result =item .copy ()

            result ["hybrid_score"]=hybrid_score 
            result ["dense_norm"]=dense_score 
            result ["sparse_norm"]=sparse_score 

            fused .append (result )

        fused .sort (
        key =lambda x :x ["hybrid_score"],
        reverse =True 
        )

        return fused 