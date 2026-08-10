import re 
from typing import Dict ,List 


class TOCParser :
    """
    Extracts structural information from the
    'ARRANGEMENT OF SECTIONS' portion of an
    Indian statute.

    Returns:

    {
        "parts": [...],
        "chapters": [...],
        "sections": [...]
    }
    """

    def __init__ (self ):

        self .part_pattern =re .compile (
        r"^PART\s+([A-Z0-9IVXLC]+)",
        re .IGNORECASE 
        )

        self .chapter_pattern =re .compile (
        r"^CHAPTER\s+([IVXLCDM]+)",
        re .IGNORECASE 
        )

        self .section_pattern =re .compile (
        r"^(\d+)\.\s+(.+)$"
        )

    def extract (
    self ,
    pages :List [Dict ]
    )->Dict :

        structure ={

        "parts":[],

        "chapters":[],

        "sections":[]

        }

        toc_started =False 

        current_part =None 

        current_chapter =None 

        pending_section =None 

        for page in pages :

            page_text =page .get (
            "text",
            ""
            )

            for raw_line in page_text .splitlines ():

                line =raw_line .strip ()

                if not line :
                    continue 

                upper =line .upper ()

                if not toc_started :

                    if (
                    "ARRANGEMENT OF"
                    in upper 
                    ):
                        toc_started =True 

                    continue 

                if (
                "ACT NO."in upper 
                or "BE IT ENACTED"in upper 
                ):

                    if pending_section :

                        structure [
                        "sections"
                        ].append (
                        pending_section 
                        )

                    return structure 

                part_match =(
                self .part_pattern .match (
                line 
                )
                )

                if part_match :

                    current_part ={

                    "number":
                    part_match .group (1 ),

                    "title":
                    "",

                    "chapters":
                    []

                    }

                    structure [
                    "parts"
                    ].append (
                    current_part 
                    )

                    continue 

                chapter_match =(
                self .chapter_pattern .match (
                line 
                )
                )

                if chapter_match :

                    current_chapter ={

                    "number":
                    chapter_match .group (1 ),

                    "title":
                    "",

                    "part":
                    (
                    current_part [
                    "number"
                    ]
                    if current_part 
                    else None 
                    )

                    }

                    structure [
                    "chapters"
                    ].append (
                    current_chapter 
                    )

                    if current_part :

                        current_part [
                        "chapters"
                        ].append (
                        chapter_match .group (1 )
                        )

                    continue 

                if (
                current_chapter 
                and current_chapter [
                "title"
                ]==""
                and not upper .startswith (
                "SECTIONS"
                )
                ):

                    if (
                    not self .part_pattern .match (
                    line 
                    )
                    and not self .chapter_pattern .match (
                    line 
                    )
                    and not self .section_pattern .match (
                    line 
                    )
                    ):

                        current_chapter [
                        "title"
                        ]=line 

                        continue 

                if upper in {

                "SECTIONS",

                "SECTIONS.",

                "ARRANGEMENT OF SECTIONS",

                "________"

                }:

                    continue 

                section_match =(
                self .section_pattern .match (
                line 
                )
                )

                if section_match :


                    if pending_section :

                        structure [
                        "sections"
                        ].append (
                        pending_section 
                        )

                    title =(
                    section_match 
                    .group (2 )
                    .strip ()
                    )

                    title =re .sub (
                    r"\.{2,}\s*\d+$",
                    "",
                    title 
                    ).strip ()

                    pending_section ={

                    "number":
                    section_match .group (1 ),

                    "title":
                    title ,

                    "chapter":
                    (
                    current_chapter [
                    "number"
                    ]
                    if current_chapter 
                    else None 
                    ),

                    "part":
                    (
                    current_part [
                    "number"
                    ]
                    if current_part 
                    else None 
                    )

                    }

                    continue 

                if pending_section :


                    if re .match (
                    r"""
                        ^(THE\s+)?
                        (FIRST|SECOND|THIRD|FOURTH|FIFTH)
                        \s+SCHEDULE
                        """,
                    upper ,
                    re .IGNORECASE |re .VERBOSE 
                    ):

                        structure [
                        "sections"
                        ].append (
                        pending_section 
                        )

                        pending_section =None 

                        continue 


                    if re .match (
                    r"^\d+\s+THE\s+",
                    upper 
                    ):

                        continue 


                    if (
                    not self .part_pattern .match (
                    line 
                    )
                    and not self .chapter_pattern .match (
                    line 
                    )
                    and not self .section_pattern .match (
                    line 
                    )
                    ):

                        pending_section [
                        "title"
                        ]+=(
                        " "
                        +line 
                        )

                        continue 

        if pending_section :

            structure [
            "sections"
            ].append (
            pending_section 
            )

        return structure 