import faiss 
from pathlib import Path 


class FAISSLoader :

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .index_path =(
        self .project_root 
        /"data"
        /"indexes"
        /"dense.index"
        )



    def load (self ):

        if not self .index_path .exists ():

            raise FileNotFoundError (

            f"Index not found: {self .index_path }"

            )

        print (

        "Loading FAISS index..."

        )

        index =faiss .read_index (

        str (self .index_path )

        )

        print (

        f"Loaded {index .ntotal } vectors."

        )

        return index 