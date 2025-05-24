from typing import Literal, Optional
from discord import app_commands

# Course Removal Constants
NOT_FOUND: int = -1
AMBIGUOUS: int = -2

# Discord Constants
COURSE_NUMBERS = app_commands.Range[int, 1000, 99999]
YEARS = Optional[app_commands.Range[int, 2025, 2125]]
TERMS = Optional[Literal["Spring Term", "Summer Term", "Fall Term"]]

SESSIONS = Optional[
    Literal[
        "10 Week",
        "Eight Week - First",
        "Eight Week - Second",
        "Eleven Week",
        "Five Week - First",
        "Five Week - Second",
        "Five Week - Third",
        "Four Week - First",
        "Four Week - Second",
        "Four Week - Third",
        "Less Than 3 Week",
        "Nine Week - First",
        "Nine Week - Second",
        "Regular Academic Session",
        "Second Session",
        "Seven Week - First",
        "Seven Week - Second",
        "Six Week - First",
        "Six Week - Second",
        "Three Week - First",
        "Three Week - Second",
        "Three Week - Third",
        "Twelve Week",
        "Winter"
    ]
]

INSTITUTIONS = Optional[
    Literal[
        "Baruch College",
        "Borough of Manhattan CC",
        "Bronx CC",
        "Brooklyn College",
        "City College",
        "College of Staten Island",
        "Graduate Center",
        "Guttman CC",
        "Hostos CC",
        "Hunter College",
        "John Jay College",
        "Kingsborough CC",
        "LaGuardia CC",
        "Lehman College",
        "Medgar Evers College",
        "NYC College of Technology",
        "Queens College",
        "Queensborough CC",
        "School of Journalism",
        "School of Labor&Urban Studies",
        "School of Law",
        "School of Medicine",
        "School of Professional Studies",
        "School of Public Health",
        "York College"
    ]
]


# Constants for scraping
HEADERS: dict[str, str] = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36" }
DEFAULT_INSTITUTION: str = "Queens College"

COLLEGE_CODES: dict[str, str] = {
    "Baruch College": "BAR01",
    "Borough of Manhattan CC": "BMC01",
    "Bronx CC": "BCC01",
    "Brooklyn College": "BKL01",
    "City College": "CTY01",
    "College of Staten Island": "CSI01",
    "Graduate Center": "GRD01",
    "Guttman CC": "NCC01",
    "Hostos CC": "HOS01",
    "Hunter College": "HTR01",
    "John Jay College": "JJC01",
    "Kingsborough CC": "KCC01",
    "LaGuardia CC": "LAG01",
    "Lehman College": "LEH01",
    "Macaulay Honors College": "MHC01",
    "Medgar Evers College": "MEC01",
    "NYC College of Technology": "NYT01",
    "Queens College": "QNS01",
    "Queensborough CC": "QCC01",
    "School of Journalism": "SOJ01",
    "School of Labor&Urban Studies": "SLU01",
    "School of Law": "LAW01",
    "School of Medicine": "MED01",
    "School of Professional Studies": "SPS01",
    "School of Public Health": "SPH01",
    "York College": "YRK01",
}

COLLEGE_BASE64: dict[str, str] = {
    "Baruch College": "QmFydWNoIENvbGxlZ2U=",
    "Borough of Manhattan CC": "Qm9yb3VnaCBvZiBNYW5oYXR0YW4gQ0M=",
    "Bronx CC": "QnJvbnggQ0M=",
    "Brooklyn College": "QnJvb2tseW4gQ29sbGVnZQ==",
    "City College": "Q2l0eSBDb2xsZWdl",
    "College of Staten Island": "Q29sbGVnZSBvZiBTdGF0ZW4gSXNsYW5k",
    "Graduate Center": "R3JhZHVhdGUgQ2VudGVy",
    "Guttman CC": "R3V0dG1hbiBDQw==",
    "Hostos CC": "SG9zdG9zIEND",
    "Hunter College": "SHVudGVyIENvbGxlZ2U=",
    "John Jay College": "Sm9obiBKYXkgQ29sbGVnZQ==",
    "Kingsborough CC": "S2luZ3Nib3JvdWdoIEND",
    "LaGuardia CC": "TGFHdWFyZGlhIEND",
    "Lehman College": "TGVobWFuIENvbGxlZ2U=",
    "Macaulay Honors College": "TWFjYXVsYXkgSG9ub3JzIENvbGxlZ2U=",
    "Medgar Evers College": "TWVkZ2FyIEV2ZXJzIENvbGxlZ2U=",
    "NYC College of Technology": "TllDIENvbGxlZ2Ugb2YgVGVjaG5vbG9neQ==",
    "Queens College": "UXVlZW5zIENvbGxlZ2U=",
    "Queensborough CC": "UXVlZW5zYm9yb3VnaCBDQw==",
    "School of Journalism": "U2Nob29sIG9mIEpvdXJuYWxpc20=",
    "School of Labor&Urban Studies": "U2Nob29sIG9mIExhYm9yJlVyYmFuIFN0dWRpZXM=",
    "School of Law": "U2Nob29sIG9mIExhdw==",
    "School of Medicine": "U2Nob29sIG9mIE1lZGljaW5l",
    "School of Professional Studies": "U2Nob29sIG9mIFByb2Zlc3Npb25hbCBTdHVkaWVz",
    "School of Public Health": "U2Nob29sIG9mIFB1YmxpYyBIZWFsdGg=",
    "York College": "WW9yayBDb2xsZWdl"
}

SESSION_BASE64: dict[str, str] = {
    "10 Week": "MTBX",
    "Eight Week - First": "OFcx",
    "Eight Week - Second": "OFcy",
    "Eleven Week": "MTFX",
    "Five Week - First": "NVcx",
    "Five Week - Second": "NVcy",
    "Five Week - Third": "NVcz",
    "Four Week - First": "NFcx",
    "Four Week - Second": "NFcy",
    "Four Week - Third": "NFcz",
    "Less Than 3 Week": "TFQz",
    "Nine Week - First": "OVcx",
    "Nine Week - Second": "OVcy",
    "Regular Academic Session": "MQ==",
    "Second Session": "Mg==",
    "Seven Week - First": "N1cx",
    "Seven Week - Second": "N1cy",
    "Six Week - First": "Nlcx",
    "Six Week - Second": "Nlcy",
    "Three Week - First": "M1cx",
    "Three Week - Second": "M1cy",
    "Three Week - Third": "M1cz",
    "Twelve Week": "MTJX",
    "Winter": "V0lO",
}