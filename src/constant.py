import os
from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
YEAR_OF_STUDY = os.getenv('YEAR')

if not YEAR_OF_STUDY.isdigit():
    raise TypeError("The desired year of study (YEAR parameter) must be an integer.")

PLANNING_URL = f"https://servif-cocktail.insa-lyon.fr/EdT/{YEAR_OF_STUDY}IF.php"
INSA_URL = "https://login.insa-lyon.fr/cas/login"
