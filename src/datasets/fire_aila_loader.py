from pathlib import Path 


class FIREAILALoader :

    def __init__ (self ):

        self .project_root =Path (__file__ ).resolve ().parents [2 ]

        self .dataset_dir =(
        self .project_root 
        /"data"
        /"datasets"
        /"fire_aila"
        )

        self .statutes_dir =(
        self .dataset_dir 
        /"Object_statutes"
        )

        self .query_file =(
        self .dataset_dir 
        /"Query_doc.txt"
        )

        self .judgment_file =(
        self .dataset_dir 
        /"relevance_judgments_statutes.txt"
        )

    def load_statutes (self ):

        statutes =[]

        for path in sorted (
        self .statutes_dir .glob ("S*.txt"),
        key =lambda p :int (p .stem [1 :])
        ):

            title =""
            description =""

            with open (
            path ,
            "r",
            encoding ="utf-8",
            errors ="ignore"
            )as f :

                for line in f :

                    line =line .strip ()

                    if line .startswith ("Title:"):

                        title =line [
                        len ("Title:"):
                        ].strip ()

                    elif line .startswith ("Desc:"):

                        description =line [
                        len ("Desc:"):
                        ].strip ()

            statutes .append ({

            "id":path .stem ,

            "title":title ,

            "text":description ,

            })

        return statutes 

    def load_queries (self ):

        queries =[]

        with open (
        self .query_file ,
        "r",
        encoding ="utf-8",
        errors ="ignore"
        )as f :

            for line in f :

                line =line .strip ()

                if not line :
                    continue 

                parts =line .split (
                "||",
                1 
                )

                if len (parts )!=2 :
                    continue 

                query_id =parts [0 ].strip ()
                query_text =parts [1 ].strip ()

                queries .append ({

                "id":query_id ,

                "query":query_text ,

                "relevant_ids":[]

                })

        return queries 

    def load_relevance (self ):

        relevance ={}

        with open (
        self .judgment_file ,
        "r",
        encoding ="utf-8",
        errors ="ignore"
        )as f :

            for line in f :

                line =line .strip ()

                if not line :
                    continue 

                parts =line .split ()

                if len (parts )<4 :
                    continue 

                query_id =parts [0 ]
                statute_id =parts [2 ]
                label =parts [3 ]

                if label !="1":
                    continue 

                if query_id not in relevance :

                    relevance [query_id ]=[]

                relevance [query_id ].append (
                statute_id 
                )

        return relevance 

    def load (self ):

        statutes =self .load_statutes ()

        queries =self .load_queries ()

        relevance =self .load_relevance ()

        for query in queries :

            query ["relevant_ids"]=relevance .get (
            query ["id"],
            []
            )

        return {

        "statutes":statutes ,

        "queries":queries 

        }

if __name__ =="__main__":

    loader =FIREAILALoader ()

    data =loader .load ()

    print ("="*60 )
    print ("FIRE AILA DATASET")
    print ("="*60 )

    print (
    f"Statutes : {len (data ['statutes'])}"
    )

    print (
    f"Queries  : {len (data ['queries'])}"
    )

    print ()

    for query in data ["queries"][:3 ]:

        print (
        f"ID: {query ['id']}"
        )

        print (
        f"Query: {query ['query'][:200 ]}"
        )

        print (
        f"Relevant statutes: "
        f"{query ['relevant_ids']}"
        )

        print ("-"*60 )