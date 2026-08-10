import json 
from pathlib import Path 

import fitz 
import pandas as pd 


class PDFExtractor :

    def __init__ (self ):

        self .project_root =Path (__file__ ).resolve ().parents [2 ]

        self .manifest_path =(
        self .project_root 
        /"data"
        /"source_manifest.csv"
        )

        self .raw_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"raw"
        )

        self .output_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"extracted"
        )

        self .output_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )

        self .stats =[]



    def load_manifest (self ):

        return pd .read_csv (
        self .manifest_path 
        )



    def extract_pdf (
    self ,
    pdf_path 
    ):

        document =fitz .open (pdf_path )

        pages =[]

        total_characters =0 
        total_words =0 

        for page_number ,page in enumerate (document ,start =1 ):

            text =page .get_text ("text")

            pages .append ({

            "page":page_number ,

            "text":text 

            })

            total_characters +=len (text )

            total_words +=len (text .split ())

        document .close ()

        return (
        pages ,
        total_characters ,
        total_words 
        )

    def save_pages (
    self ,
    document_name ,
    pages 
    ):

        output_folder =(
        self .output_dir 
        /document_name 
        )

        output_folder .mkdir (
        parents =True ,
        exist_ok =True 
        )

        output_path =(
        output_folder 
        /"pages.json"
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            pages ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )


    def save_statistics (self ):

        output_path =(
        self .output_dir 
        /"extraction_stats.json"
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            self .stats ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )



    def run (self ):

        manifest =self .load_manifest ()

        print ("="*60 )
        print ("PDF EXTRACTOR")
        print ("="*60 )

        for _ ,row in manifest .iterrows ():

            pdf_path =(
            self .raw_dir 
            /row ["filename"]
            )

            if not pdf_path .exists ():

                print (f"✗ Missing: {row ['filename']}")
                continue 

            pages ,characters ,words =self .extract_pdf (
            pdf_path 
            )

            document_name =Path (
            row ["filename"]
            ).stem 

            self .save_pages (
            document_name ,
            pages 
            )

            self .stats .append ({

            "document_id":row ["document_id"],

            "title":row ["title"],

            "pages":len (pages ),

            "characters":characters ,

            "words":words ,

            "average_words_per_page":round (
            words /len (pages ),
            2 
            )if len (pages )else 0 

            })

            print (
            f"✓ {document_name } | "
            f"{len (pages )} pages | "
            f"{words } words"
            )

        self .save_statistics ()

        print ("\n"+"="*60 )
        print ("Extraction Complete")
        print ("="*60 )

if __name__ =="__main__":

    extractor =PDFExtractor ()

    extractor .run ()