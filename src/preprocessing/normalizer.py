import json 
from pathlib import Path 
import re 

class Normalizer :

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .input_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"parsed"
        )

        self .output_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"normalized"
        )

        self .output_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )

        self .stats =[]

    def load_document (
    self ,
    filename 
    ):

        with open (
        self .input_dir /filename ,
        "r",
        encoding ="utf-8"
        )as f :

            return json .load (f )

    def save_document (
    self ,
    filename ,
    data 
    ):

        with open (
        self .output_dir /filename ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            data ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )

    def normalize_unicode (
    self ,
    text 
    ):

        replacements ={

        "“":'"',
        "”":'"',

        "‘":"'",
        "’":"'",

        "–":"-",
        "—":"-",

        "\u00a0":" "

        }

        for old ,new in replacements .items ():

            text =text .replace (
            old ,
            new 
            )

        return text 

    def normalize_spaces (
    self ,
    text 
    ):

        lines =[]

        for line in text .splitlines ():

            line =re .sub (
            r"[ \t]+",
            " ",
            line 
            )

            lines .append (
            line .strip ()
            )

        return "\n".join (lines )

    def normalize_blank_lines (
    self ,
    text 
    ):

        text =re .sub (
        r"\n{3,}",
        "\n\n",
        text 
        )

        return text .strip ()

    def normalize_text (
    self ,
    text 
    ):

        if not text :

            return ""

        text =str (text )

        text =self .normalize_unicode (
        text 
        )

        text =self .normalize_spaces (
        text 
        )

        text =self .normalize_blank_lines (
        text 
        )

        return text 

    def normalize_document (
    self ,
    document 
    ):

        if isinstance (
        document .get ("text"),
        str 
        ):

            document ["text"]=(
            self .normalize_text (
            document ["text"]
            )
            )

        sections =document .get (
        "sections"
        )

        if isinstance (
        sections ,
        list 
        ):

            for section in sections :

                if isinstance (
                section ,
                dict 
                ):

                    if isinstance (
                    section .get ("text"),
                    str 
                    ):

                        section ["text"]=(
                        self .normalize_text (
                        section ["text"]
                        )
                        )

        pages =document .get (
        "pages"
        )

        if isinstance (
        pages ,
        list 
        ):

            for page in pages :

                if isinstance (
                page ,
                dict 
                ):

                    if isinstance (
                    page .get ("text"),
                    str 
                    ):

                        page ["text"]=(
                        self .normalize_text (
                        page ["text"]
                        )
                        )

        return document 

    def save_statistics (self ):

        output_path =(
        self .output_dir 
        /"normalization_stats.json"
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

        print ("="*60 )
        print ("GENERIC NORMALIZER")
        print ("="*60 )

        files =sorted (
        self .input_dir .glob ("*.json")
        )

        for file in files :

            if file .name .endswith (
            "_stats.json"
            ):
                continue 

            document =(
            self .load_document (
            file .name 
            )
            )

            before_text =(
            self .collect_text (
            document 
            )
            )

            before_chars =len (
            before_text 
            )

            document =(
            self .normalize_document (
            document 
            )
            )

            after_text =(
            self .collect_text (
            document 
            )
            )

            after_chars =len (
            after_text 
            )

            self .save_document (
            file .name ,
            document 
            )

            self .stats .append ({

            "document":
            file .stem ,

            "characters_before":
            before_chars ,

            "characters_after":
            after_chars ,

            "characters_removed":
            before_chars -after_chars 

            })

            print (
            f"✓ {file .stem } | "
            f"{before_chars } → "
            f"{after_chars } characters"
            )

        self .save_statistics ()

        print ("\n"+"="*60 )
        print ("Normalization Complete")
        print ("="*60 )

    def collect_text (
    self ,
    document 
    ):

        texts =[]

        if isinstance (
        document .get ("text"),
        str 
        ):

            texts .append (
            document ["text"]
            )

        sections =document .get (
        "sections"
        )

        if isinstance (
        sections ,
        list 
        ):

            for section in sections :

                if isinstance (
                section ,
                dict 
                ):

                    text =section .get (
                    "text",
                    ""
                    )

                    if isinstance (
                    text ,
                    str 
                    ):

                        texts .append (text )

        pages =document .get (
        "pages"
        )

        if isinstance (
        pages ,
        list 
        ):

            for page in pages :

                if isinstance (
                page ,
                dict 
                ):

                    text =page .get (
                    "text",
                    ""
                    )

                    if isinstance (
                    text ,
                    str 
                    ):

                        texts .append (text )

        return "\n".join (texts )

if __name__ =="__main__":

    normalizer =Normalizer ()

    normalizer .run ()