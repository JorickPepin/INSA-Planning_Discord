import os
from dotenv import load_dotenv

load_dotenv()

# USER
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')

YEAR_OF_STUDY = os.getenv('YEAR')

# LINKS
INSA_URL = "https://login.insa-lyon.fr/cas/login"
PLANNING_URL = f"https://servif-cocktail.insa-lyon.fr/EdT/{YEAR_OF_STUDY}IF.php"
