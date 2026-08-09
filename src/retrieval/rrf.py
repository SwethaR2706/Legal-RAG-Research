class ReciprocalRankFusion :

    def __init__ (self ,k =60 ):

        self .k =k 

    def fuse (
    self ,
    dense_results ,
    sparse_results 
    ):

        scores ={}
        documents ={}

        for rank ,item in enumerate (
        dense_results ,
        start =1 
        ):

            key =item ["id"]

            scores [key ]=(
            scores .get (key ,0.0 )
            +1.0 /(self .k +rank )
            )

            documents [key ]=item 

        for rank ,item in enumerate (
        sparse_results ,
        start =1 
        ):

            key =item ["id"]

            scores [key ]=(
            scores .get (key ,0.0 )
            +1.0 /(self .k +rank )
            )

            documents [key ]=item 
            
        fused =[]

        for key ,score in scores .items ():

            item =documents [key ].copy ()

            item ["rrf_score"]=float (
            score 
            )

            fused .append (item )

        fused .sort (
        key =lambda x :x ["rrf_score"],
        reverse =True 
        )

        return fused 