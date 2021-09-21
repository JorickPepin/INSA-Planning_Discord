import os
from dotenv import load_dotenv

load_dotenv()

#- user
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
YEAR_OF_STUDY = os.getenv('YEAR')

if not YEAR_OF_STUDY.isdigit():
    raise TypeError("The desired year of study (YEAR parameter) must be an integer.")


#- links
PLANNING_URL = f"https://servif-cocktail.insa-lyon.fr/EdT/{YEAR_OF_STUDY}IF.php"
INSA_URL = "https://login.insa-lyon.fr/cas/login"


#- utils
LAUNCH_TIME = "17:30"

# The structure of the timetable website makes it difficult to recover the duration of a class slot.
# The following dictionnary contains the main slots in the form {number of colspan => lesson duration in minutes}.
# If the slot is not available here, an algorithm is implemented to determine its duration but it does not have
# 100% accuracy (possible shift of 15 minutes).
# This solution is not optimal so do not hesitate to contribute if you find a better one.
COLSPAN_DURATION = {
    4: 60,
    5: 60,
    6: 75,
    7: 90,
    8: 90,
    9: 120,
    10: 120,
    14: 180,
    16: 195,
    19: 240,
    22: 270,
    39: 240,
    49: 360
}
