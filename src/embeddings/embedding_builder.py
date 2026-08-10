import json 
from pathlib import Path 

import numpy as np 

from src .embeddings .bge_embedder import BGEEmbedder 

class EmbeddingBuilder :

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .chunk_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"chunks"
        )

        self .output_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"embeddings"
        )

        self .output_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )

        self .embedder =BGEEmbedder ()
    def load_chunks (self ):

        texts =[]
        metadata =[]

        json_files =sorted (
        self .chunk_dir .glob ("*.json")
        )

        print (
        f"\nFound {len (json_files )} chunk files."
        )

        for file in json_files :

            with open (
            file ,
            "r",
            encoding ="utf-8"
            )as f :

                chunks =json .load (f )

            if not isinstance (chunks ,list ):
                print (
                f"Skipping invalid file: {file .name }"
                )
                continue 

            for chunk in chunks :

                text =chunk .get (
                "text",
                ""
                ).strip ()

                if not text :
                    continue 

                document =chunk .get (
                "document",
                file .stem 
                )


                embedding_text =text 

                texts .append (
                embedding_text 
                )


                item ={
                "chunk_id":chunk .get (
                "chunk_id"
                ),

                "document":document ,

                "text":text 
                }


                optional_fields =[
                "chapter",
                "section_number",
                "section_title",
                "chunk_index",
                "word_count"
                ]

                for field in optional_fields :

                    if field in chunk :

                        item [field ]=chunk [field ]

                metadata .append (item )

        print (
        f"Loaded {len (texts )} chunks."
        )

        return texts ,metadata 

    def generate_embeddings (
    self ,
    texts 
    ):

        print (
        "\nGenerating embeddings..."
        )

        vectors =self .embedder .embed_batch (
        texts ,
        batch_size =8 
        )

        return vectors 

    def save_embeddings (
    self ,
    vectors 
    ):

        output_path =(
        self .output_dir 
        /"dense_vectors.npy"
        )

        np .save (
        output_path ,
        vectors 
        )

        print (
        f"Embeddings saved to: {output_path }"
        )

    def save_metadata (
    self ,
    metadata 
    ):

        output_path =(
        self .output_dir 
        /"metadata.json"
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            metadata ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )

        print (
        f"Metadata saved to: {output_path }"
        )

    def save_embedding_info (
    self ,
    vectors 
    ):

        info ={

        "model":self .embedder .model_name ,

        "dimension":int (
        vectors .shape [1 ]
        ),

        "total_chunks":int (
        vectors .shape [0 ]
        ),

        "batch_size":8 ,

        "normalized":True 

        }

        output_path =(
        self .output_dir 
        /"embedding_info.json"
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            info ,
            f ,
            indent =4 
            )

        print (
        f"Embedding information saved to: "
        f"{output_path }"
        )

    def run (self ):

        print ("="*60 )
        print ("RESEARCH EMBEDDING BUILDER")
        print ("="*60 )

        texts ,metadata =(
        self .load_chunks ()
        )

        if not texts :

            raise RuntimeError (
            "No valid chunks found."
            )

        vectors =(
        self .generate_embeddings (
        texts 
        )
        )

        print (
        f"\nEmbedding shape: "
        f"{vectors .shape }"
        )

        self .save_embeddings (
        vectors 
        )

        self .save_metadata (
        metadata 
        )

        self .save_embedding_info (
        vectors 
        )

        print ("\n"+"="*60 )
        print ("Embedding Complete")
        print ("="*60 )

        print (
        f"Chunks     : {len (texts )}"
        )

        print (
        f"Embeddings : {vectors .shape }"
        )

        print (
        f"Output     : {self .output_dir }"
        )

if __name__ =="__main__":

    builder =EmbeddingBuilder ()

    builder .run ()