from typing import Literal, Union
from discord import app_commands

YEARS = app_commands.Range[int, 2025, 2125]
TERMS = Literal['Spring Term', 'Summer Term', 'Fall Term']
COURSE_NUMBERS = app_commands.Range[int, 1000, 99999]

SESSIONS = Union[
    None,
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

INSTITUTIONS = Union[
    None,
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