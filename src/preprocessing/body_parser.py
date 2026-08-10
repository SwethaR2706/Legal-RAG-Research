import re 

class BodyParser :

    def __init__ (self ):

        self .section_pattern =re .compile (
        r"""
            ^\s*
            (?:\d+\[)?
            (\d+[A-Z]?)
            (?:\.|\s{2,})
            \s*
            (.+)$
            """,
        re .VERBOSE 
        )

        self .chapter_pattern =re .compile (
        r"^CHAPTER\s+([IVXLCDM]+)",
        re .IGNORECASE 
        )

        self .header_keywords =[
        "GAZETTE OF INDIA",
        "EXTRAORDINARY",
        "MINISTRY OF LAW",
        "LEGISLATIVE DEPARTMENT",
        "REGISTERED NO",
        "PART I",
        "PART II",
        "PART III",
        "PART IV",
        ]

        self .running_headers =[
        "THE ARMS ACT",
        "THE NARCOTIC DRUGS",
        "THE JUVENILE JUSTICE",
        "THE PROTECTION OF CHILDREN",
        ]

    def clean_line (self ,text ):

        text =text .strip ()

        text =re .sub (
        r"^\d+\*\[(\d+[A-Z]?)\.",
        r"\1.",
        text 
        )

        text =re .sub (
        r"^\d+\[(\d+[A-Z]?)\s+",
        r"\1. ",
        text 
        )

        if not text :
            return None 

        upper =text .upper ()


        if re .fullmatch (r"\d+",text ):
            return None 


        if re .fullmatch (r"[-_=]{3,}",text ):
            return None 


        if any (
        keyword in upper 
        for keyword in self .header_keywords 
        ):
            return None 


        if any (
        upper .startswith (header )
        for header in self .running_headers 
        ):
            return None 


        if re .match (
        r"^SEC\.",
        upper 
        ):
            return None 


        if re .match (
        r"""
            ^\d+\.\s*
            (
                INS\.?
                |SUBS\.?
                |INSERTED
                |INSERTED\ BY
                |SUBSTITUTED
                |SUBSTITUTED\ BY
                |OMITTED
                |REPEALED
                |RENUMBERED
                |VIDE
            )
            """,
        text ,
        re .IGNORECASE |re .VERBOSE 
        ):
            return None 

        return text 

    def parse (self ,pages ):

        sections =[]

        current_section =None 
        current_text =[]

        current_chapter =None 

        body_started =False 

        previous_number =0 

        for page in pages :

            page_number =page .get (
            "page",
            None 
            )

            page_text =page .get (
            "text",
            ""
            )

            for raw_line in page_text .splitlines ():

                text =self .clean_line (
                raw_line 
                )

                if text is None :
                    continue 

                upper =text .upper ()

                if not body_started :

                    if (
                    "BE IT ENACTED"in upper 
                    or upper .startswith ("CHAPTER")
                    ):
                        body_started =True 

                    else :
                        continue 

                chapter =(
                self .chapter_pattern .match (
                text 
                )
                )

                if chapter :

                    current_chapter =chapter .group (0 )

                    continue 

                match =(
                self .section_pattern .match (
                text 
                )
                )

                if (
                match 
                and current_chapter is not None 
                ):

                    section_number =(
                    match .group (1 )
                    )

                    title =(
                    match .group (2 )
                    .strip (" -.")
                    )

                    try :

                        numeric_match =re .match (
                        r"\d+",
                        section_number 
                        )

                        current_number =int (
                        numeric_match .group ()
                        )


                        if (
                        current_number 
                        <previous_number 
                        ):
                            continue 


                        if (
                        previous_number >0 
                        and current_number 
                        >previous_number +50 
                        ):
                            continue 

                        previous_number =(
                        current_number 
                        )

                    except Exception :
                        pass 

                    if current_section is not None :

                        current_section ["text"]=(
                        "\n".join (
                        current_text 
                        ).strip ()
                        )

                        sections .append (
                        current_section 
                        )

                    current_section ={

                    "number":
                    section_number ,

                    "title":
                    title ,

                    "chapter":
                    current_chapter ,

                    "part":
                    None ,

                    "start_page":
                    page_number ,

                    "end_page":
                    page_number ,

                    "text":
                    ""

                    }

                    current_text =[text ]

                    continue 

                if current_section is not None :

                    current_text .append (
                    text 
                    )

                    current_section [
                    "end_page"
                    ]=page_number 

        if current_section is not None :

            current_section ["text"]=(
            "\n".join (
            current_text 
            ).strip ()
            )

            sections .append (
            current_section 
            )

        return sections 