from src .config import hf_config 
from sentence_transformers import SentenceTransformer 
import torch 
import numpy as np 



class BGEEmbedder :
    """
    Wrapper around the BAAI BGE-M3 embedding model.
    Responsible only for generating embeddings.
    """

    def __init__ (
    self ,
    model_name :str ="BAAI/bge-base-en-v1.5",
    device :str |None =None 
    ):
        self .model_name =model_name 

        if device is None :
            device =(
            "cuda"
            if torch .cuda .is_available ()
            else "cpu"
            )

        self .device =device 

        print (f"Loading embedding model: {model_name }")
        print (f"Using device: {self .device }")

        self .model =SentenceTransformer (
        model_name ,
        device =self .device 
        )



    def embed (
    self ,
    text :str ,
    normalize :bool =True 
    )->np .ndarray :
        """
        Generate embedding for a single text.
        """

        embedding =self .model .encode (
        text ,
        normalize_embeddings =normalize ,
        convert_to_numpy =True ,
        show_progress_bar =False 
        )

        return embedding 



    def embed_batch (
    self ,
    texts :list [str ],
    batch_size :int =32 ,
    normalize :bool =True 
    )->np .ndarray :
        """
        Generate embeddings for multiple texts.
        """

        embeddings =self .model .encode (
        texts ,
        batch_size =batch_size ,
        normalize_embeddings =normalize ,
        convert_to_numpy =True ,
        show_progress_bar =True 
        )

        return embeddings 
if __name__ =="__main__":

    embedder =BGEEmbedder ()

    vector =embedder .embed (
    "Identity theft is punishable under the Information Technology Act."
    )

    print ("Embedding Dimension:",len (vector ))
    print ("Embedding Dimension:",embedder .embedding_dimension ())