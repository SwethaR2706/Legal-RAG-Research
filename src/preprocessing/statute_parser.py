import json 
import re 
from pathlib import Path 

from .body_parser import BodyParser 
from .toc_parser import TOCParser 

class StatuteParser :

    def __init__ (self ):

        self .project_root =(
        Path (__file__ ).resolve ().parents [2 ]
        )

        self .extracted_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"extracted"
        )

        self .output_dir =(
        self .project_root 
        /"data"
        /"corpus"
        /"parsed"
        )

        self .output_dir .mkdir (
        parents =True ,
        exist_ok =True 
        )

        self .body_parser =BodyParser ()

        self .toc_parser =TOCParser ()

        self .section_pattern =re .compile (
        r"""
            ^\s*
            (?:\d+\[)?
            (\d+[A-Z]?)
            (?:\.|\s{2,})
            """,
        re .VERBOSE 
        )

    def load_pages (
    self ,
    document_name 
    ):

        path =(
        self .extracted_dir 
        /document_name 
        /"pages.json"
        )

        if not path .exists ():

            raise FileNotFoundError (
            f"Extracted pages not found: {path }"
            )

        with open (
        path ,
        "r",
        encoding ="utf-8"
        )as f :

            return json .load (f )

    def flatten_body (
    self ,
    pages 
    ):

        lines =[]

        body_started =False 

        for page in pages :

            page_number =page .get (
            "page"
            )

            for raw in page .get (
            "text",
            ""
            ).splitlines ():

                text =raw .strip ()

                if not text :
                    continue 

                if not body_started :

                    if (
                    "BE IT ENACTED"
                    in text .upper ()
                    ):

                        body_started =True 

                    continue 

                lines .append ({

                "page":
                page_number ,

                "text":
                text 

                })

        return lines 

    def parse_document (
    self ,
    pages ,
    structure 
    ):

        body =self .flatten_body (
        pages 
        )

        toc_sections =structure .get (
        "sections",
        []
        )

        parsed_sections =[]

        expected_index =0 

        current_section =None 

        current_text =[]

        for line in body :

            text =line ["text"]


            text =re .sub (
            r"^\d+\[(\d+[A-Z]?)\s+",
            r"\1. ",
            text 
            )

            page =line ["page"]

            if (
            expected_index 
            >=len (toc_sections )
            ):

                if current_section is not None :

                    current_section [
                    "text"
                    ]=(
                    "\n".join (
                    current_text 
                    ).strip ()
                    )

                    parsed_sections .append (
                    current_section 
                    )

                    current_section =None 

                break 

            expected =(
            toc_sections [
            expected_index 
            ]
            )

            expected_number =(
            expected ["number"]
            )

            match =(
            self .section_pattern .search (
            text 
            )
            )

            if match :

                found_number =(
                match .group (1 )
                )

                if (
                found_number 
                ==expected_number 
                ):

                    if current_section is not None :

                        current_section [
                        "text"
                        ]=(
                        "\n".join (
                        current_text 
                        ).strip ()
                        )

                        parsed_sections .append (
                        current_section 
                        )

                    title =expected .get (
                    "title",
                    ""
                    )

                    title =re .split (
                    r"""
                        \bTHE\s+
                        (FIRST|SECOND|THIRD|FOURTH)
                        \s+SCHEDULE\b
                        """,
                    title ,
                    flags =(
                    re .IGNORECASE 
                    |re .VERBOSE 
                    )
                    )[0 ].strip ()

                    title =re .sub (
                    r"""
                        \s+\d+\s+
                        THE\s+BHARATIYA.*$
                        """,
                    "",
                    title ,
                    flags =re .IGNORECASE 
                    ).strip ()

                    current_section ={

                    "number":
                    expected .get (
                    "number"
                    ),

                    "title":
                    title ,

                    "chapter":
                    expected .get (
                    "chapter"
                    ),

                    "part":
                    expected .get (
                    "part"
                    ),

                    "start_page":
                    page ,

                    "end_page":
                    page ,

                    "text":
                    ""

                    }

                    current_text =[text ]

                    expected_index +=1 

                    continue 

            if current_section is not None :

                current_text .append (
                text 
                )

                current_section [
                "end_page"
                ]=page 

        if current_section is not None :

            current_section [
            "text"
            ]=(
            "\n".join (
            current_text 
            ).strip ()
            )

            parsed_sections .append (
            current_section 
            )

        return parsed_sections 

    def save_document (
    self ,
    document_id ,
    title ,
    source ,
    document_type ,
    filename ,
    parsed_sections 
    ):

        output ={

        "document_id":
        document_id ,

        "title":
        title ,

        "document_type":
        document_type ,

        "source":
        source ,

        "sections":
        parsed_sections 

        }

        output_path =(
        self .output_dir 
        /f"{Path (filename ).stem }.json"
        )

        with open (
        output_path ,
        "w",
        encoding ="utf-8"
        )as f :

            json .dump (
            output ,
            f ,
            indent =4 ,
            ensure_ascii =False 
            )

        return output_path 

    def parse_single_document (
    self ,
    document_id ,
    title ,
    source ,
    document_type ,
    filename 
    ):

        document_name =(
        Path (filename ).stem 
        )

        print (
        f"\nParsing {document_name }..."
        )

        pages =self .load_pages (
        document_name 
        )

        structure =(
        self .toc_parser .extract (
        pages 
        )
        )

        if structure .get (
        "sections"
        ):

            parsed_sections =(
            self .parse_document (
            pages ,
            structure 
            )
            )

        else :

            parsed_sections =(
            self .body_parser .parse (
            pages 
            )
            )

        output_path =(
        self .save_document (
        document_id ,
        title ,
        source ,
        document_type ,
        filename ,
        parsed_sections 
        )
        )

        print (
        f"✓ Parsed "
        f"{len (parsed_sections )} sections"
        )

        print (
        f"  Saved: {output_path }"
        )

        return {
        "document_id":
        document_id ,

        "title":
        title ,

        "source":
        source ,

        "document_type":
        document_type ,

        "sections":
        parsed_sections 
        }