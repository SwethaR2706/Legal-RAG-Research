import json 
from pathlib import Path 

import faiss 
import numpy as np 


class FAISSBuilder :

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .embedding_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"embeddings"
        )

        self .index_dir =(
        self .project_root 
        /"data"
        /"indexes"
        )

        self .index_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )



    def load_vectors (self ):

        print ("\nLoading embeddings...")

        vectors =np .load (
        self .embedding_dir 
        /"dense_vectors.npy"
        )

        print (
        f"Loaded {vectors .shape [0 ]} vectors "
        f"({vectors .shape [1 ]} dimensions)"
        )

        return vectors .astype (np .float32 )



    def build_index (
    self ,
    vectors 
    ):

        print ("\nBuilding FAISS index...")

        dimension =vectors .shape [1 ]

        index =faiss .IndexFlatIP (
        dimension 
        )

        index .add (vectors )

        print (
        f"Indexed {index .ntotal } vectors"
        )

        return index 



    def save_index (
    self ,
    index 
    ):

        output =(
        self .index_dir 
        /"dense.index"
        )

        faiss .write_index (
        index ,
        str (output )
        )



    def save_info (
    self ,
    vectors 
    ):

        info ={

        "index_type":"IndexFlatIP",

        "metric":"Inner Product (Cosine Similarity)",

        "dimension":int (
        vectors .shape [1 ]
        ),

        "vectors":int (
        vectors .shape [0 ]
        )

        }

        with open (

        self .index_dir 
        /"index_info.json",

        "w",

        encoding ="utf-8"

        )as f :

            json .dump (
            info ,
            f ,
            indent =4 
            )



    def run (self ):

        print ("="*60 )
        print ("FAISS INDEX BUILDER")
        print ("="*60 )

        vectors =self .load_vectors ()

        index =self .build_index (
        vectors 
        )

        print ("\nSaving index...")

        self .save_index (
        index 
        )

        self .save_info (
        vectors 
        )

        print ("\n"+"="*60 )
        print ("Index Complete")
        print ("="*60 )

        print (
        f"Vectors   : {vectors .shape [0 ]}"
        )

        print (
        f"Dimension : {vectors .shape [1 ]}"
        )

        print (
        f"Saved to  : {self .index_dir }"
        )




if __name__ =="__main__":

    builder =FAISSBuilder ()

    builder .run ()