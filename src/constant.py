import os
from dotenv import load_dotenv

load_dotenv()

# USER
LOGIN = os.getenv('LOGIN')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

YEAR_OF_STUDY = os.getenv('YEAR')
GROUP_OF_STUDY = os.getenv('GROUP')

# LINKS
INSA_URL = "https://login.insa-lyon.fr/cas/login"
PLANNING_URL = f"https://servif-cocktail.insa-lyon.fr/EdT/{YEAR_OF_STUDY}IF.php"
ZIMBRA_URL = f"https://zmail.insa-lyon.fr/home/{EMAIL}/calendar?fmt=ics"
