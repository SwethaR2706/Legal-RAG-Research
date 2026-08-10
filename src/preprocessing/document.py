from dataclasses import dataclass ,field 
from typing import Any ,Dict ,List 


@dataclass 
class LegalDocument :

    document_id :str 

    title :str =""

    source :str =""

    document_type :str =""

    text :str =""

    metadata :Dict [str ,Any ]=field (
    default_factory =dict 
    )

    pages :List [Dict [str ,Any ]]=field (
    default_factory =list 
    )