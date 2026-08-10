import json 
import re 
from pathlib import Path 

class Chunker :

    MAX_WORDS =350 

    OVERLAP =50 

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .input_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"normalized"
        )

        self .output_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"chunks"
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
    chunks 
    ):

        output_path =(
        self .output_dir /filename 
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            chunks ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )

    def split_into_units (
    self ,
    text 
    ):

        if not text :

            return []

        units =[
        unit .strip ()
        for unit in re .split (
        r"\n\s*\n+",
        text 
        )
        if unit .strip ()
        ]

        if not units :

            units =[
            line .strip ()
            for line in text .splitlines ()
            if line .strip ()
            ]

        return units 

    def split_large_unit (
    self ,
    words 
    ):

        chunks =[]

        start =0 

        while start <len (words ):

            end =min (
            start +self .MAX_WORDS ,
            len (words )
            )

            chunks .append (
            " ".join (
            words [start :end ]
            )
            )

            if end ==len (words ):

                break 

            start =max (
            end -self .OVERLAP ,
            start +1 
            )

        return chunks 

    def split_into_chunks (
    self ,
    text 
    ):

        units =self .split_into_units (
        text 
        )

        chunks =[]

        current =[]

        current_words =0 

        for unit in units :

            words =unit .split ()

            if len (words )>self .MAX_WORDS :

                if current :

                    chunks .append (
                    "\n".join (current )
                    )

                    current =[]

                    current_words =0 

                large_chunks =(
                self .split_large_unit (
                words 
                )
                )

                chunks .extend (
                large_chunks 
                )

                continue 
            
            if (
            current_words 
            +len (words )
            <=self .MAX_WORDS 
            ):

                current .append (unit )

                current_words +=len (words )

            else :

                if current :

                    completed =(
                    "\n".join (
                    current 
                    )
                    )

                    chunks .append (
                    completed 
                    )


                overlap_words =[]

                if (
                self .OVERLAP >0 
                and chunks 
                ):

                    previous_words =(
                    chunks [-1 ].split ()
                    )

                    overlap_words =(
                    previous_words [
                    -self .OVERLAP :
                    ]
                    )

                current =[]

                current_words =0 

                if overlap_words :

                    overlap_text =(
                    " ".join (
                    overlap_words 
                    )
                    )

                    current .append (
                    overlap_text 
                    )

                    current_words =(
                    len (overlap_words )
                    )


                current .append (
                unit 
                )

                current_words +=len (
                words 
                )

        if current :

            chunks .append (
            "\n".join (current )
            )

        return chunks 

    def get_document_text (
    self ,
    document 
    ):


        if isinstance (
        document .get ("text"),
        str 
        ):

            return [
            {
            "text":
            document ["text"],
            "metadata":
            {}
            }
            ]


        sections =document .get (
        "sections"
        )

        if isinstance (
        sections ,
        list 
        ):

            units =[]

            for section in sections :

                if not isinstance (
                section ,
                dict 
                ):

                    continue 

                text =section .get (
                "text",
                ""
                )

                if not text .strip ():

                    continue 

                units .append ({

                "text":text ,

                "metadata":{

                "chapter":
                section .get (
                "chapter"
                ),

                "section_number":
                section .get (
                "number"
                ),

                "section_title":
                section .get (
                "title"
                )

                }

                })

            return units 


        pages =document .get (
        "pages"
        )

        if isinstance (
        pages ,
        list 
        ):

            units =[]

            for page in pages :

                if not isinstance (
                page ,
                dict 
                ):

                    continue 

                text =page .get (
                "text",
                ""
                )

                if not text .strip ():

                    continue 

                units .append ({

                "text":text ,

                "metadata":{

                "page":
                page .get (
                "page"
                )

                }

                })

            return units 

        return []

    def chunk_document (
    self ,
    document_name ,
    document 
    ):

        source_units =(
        self .get_document_text (
        document 
        )
        )

        all_chunks =[]

        global_index =1 

        for source_unit in source_units :

            text =source_unit [
            "text"
            ]

            metadata =source_unit .get (
            "metadata",
            {}
            )

            chunks =(
            self .split_into_chunks (
            text 
            )
            )

            for chunk_text in chunks :

                chunk_metadata ={

                "document":
                document_name ,

                "chunk_id":
                f"{document_name }_{global_index }",

                "chunk_index":
                global_index ,

                "text":
                chunk_text ,

                "word_count":
                len (
                chunk_text .split ()
                )
                }


                for key ,value in metadata .items ():

                    if value is not None :

                        chunk_metadata [
                        key 
                        ]=value 

                all_chunks .append (
                chunk_metadata 
                )

                global_index +=1 

        return all_chunks 

    def save_statistics (self ):

        output_path =(
        self .output_dir 
        /"chunk_stats.json"
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
        print ("GENERIC CHUNKER")
        print ("="*60 )

        files =sorted (
        self .input_dir .glob (
        "*.json"
        )
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

            document_name =file .stem 

            chunks =(
            self .chunk_document (
            document_name ,
            document 
            )
            )

            self .save_document (
            file .name ,
            chunks 
            )

            word_counts =[
            chunk ["word_count"]
            for chunk in chunks 
            ]

            self .stats .append ({

            "document":
            document_name ,

            "chunks":
            len (chunks ),

            "average_chunk_words":
            round (
            sum (word_counts )
            /len (word_counts ),
            2 
            )
            if word_counts 
            else 0 ,

            "largest_chunk":
            max (word_counts )
            if word_counts 
            else 0 ,

            "smallest_chunk":
            min (word_counts )
            if word_counts 
            else 0 

            })

            print (
            f"✓ {document_name } | "
            f"{len (chunks )} chunks"
            )

        self .save_statistics ()

        print ("\n"+"="*60 )
        print ("Chunking Complete")
        print ("="*60 )


if __name__ =="__main__":

    chunker =Chunker ()

    chunker .run ()