import json 
from pathlib import Path 


class LegalBenchRAGLoader :

    def __init__ (
    self ,
    data_dir ="data/datasets/legalbench_rag"
    ):

        self .data_dir =Path (
        data_dir 
        )

        self .corpus_file =(
        self .data_dir /"corpus.jsonl"
        )

        self .qa_file =(
        self .data_dir /"qa.jsonl"
        )

    def _load_jsonl (
    self ,
    path 
    ):

        records =[]

        with open (
        path ,
        "r",
        encoding ="utf-8"
        )as file :

            for line in file :

                line =line .strip ()

                if not line :
                    continue 

                records .append (
                json .loads (line )
                )

        return records 

    def load (self ):

        if not self .corpus_file .exists ():

            raise FileNotFoundError (
            f"Corpus file not found: "
            f"{self .corpus_file }"
            )

        if not self .qa_file .exists ():

            raise FileNotFoundError (
            f"QA file not found: "
            f"{self .qa_file }"
            )

        raw_corpus =self ._load_jsonl (
        self .corpus_file 
        )

        raw_qa =self ._load_jsonl (
        self .qa_file 
        )

        corpus =[]

        for item in raw_corpus :

            corpus .append ({

            "id":
            item ["id"],

            "title":
            item .get (
            "title",
            ""
            ),

            "text":
            item .get (
            "text",
            ""
            ),

            "footnotes":
            item .get (
            "footnotes",
            ""
            )

            })

        queries =[]

        for item in raw_qa :

            relevant_id =(
            item ["relevant_passage_id"]
            )

            queries .append ({

            "id":
            str (item ["id"]),

            "query":
            item ["question"],

            "answer":
            item .get (
            "answer",
            ""
            ),

            "relevant_ids":
            [relevant_id ]

            })

        return {

        "corpus":
        corpus ,

        "queries":
        queries 

        }

def main ():

    print ("="*60 )
    print ("LEGALBENCH-RAG DATASET")
    print ("="*60 )

    loader =LegalBenchRAGLoader ()

    data =loader .load ()

    corpus =data ["corpus"]
    queries =data ["queries"]

    print (
    f"\nCorpus : {len (corpus )}"
    )

    print (
    f"Queries: {len (queries )}"
    )

    print (
    "\n"+"="*60 
    )

    print (
    "SAMPLE CORPUS DOCUMENT"
    )

    print (
    "="*60 
    )

    sample =corpus [0 ]

    print (
    f"ID: {sample ['id']}"
    )

    print (
    f"Title: {sample ['title']}"
    )

    print (
    f"Text: {sample ['text'][:300 ]}"
    )

    print (
    "\n"+"="*60 
    )

    print (
    "SAMPLE QUERY"
    )

    print (
    "="*60 
    )

    query =queries [0 ]

    print (
    f"ID: {query ['id']}"
    )

    print (
    f"Question: {query ['query']}"
    )

    print (
    f"Gold: {query ['relevant_ids']}"
    )

if __name__ =="__main__":

    main ()