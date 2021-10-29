"""
Contain environment variables and constants.
"""

import os
import locale
from dotenv import load_dotenv

load_dotenv()

#- CONFIG
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
YEAR_OF_STUDY = int(os.getenv('YEAR'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
LAUNCH_TIME = os.getenv('LAUNCH_TIME')

#- LINKS
TIMETABLE_URL = f"https://servif-cocktail.insa-lyon.fr/EdT/{YEAR_OF_STUDY}IF.php"
INSA_URL = "https://login.insa-lyon.fr/cas/login"

#- EMOJI / IMAGES
EMOJI_TIME = ":alarm_clock:"
EMOJI_PLANNING = ":calendar:"
EMOJI_TEACHER = ":teacher:"
EMOJI_PLACE = ":pushpin:"
EMOJI_LINK = ":link:"
EMOJI_GROUPS = {
    '1': ":one:",
    '2': ":two:",
    '3': ":three:",
    '4': ":four:"
}
REST_IMAGES = [
    "https://i.kym-cdn.com/entries/icons/original/000/034/981/cover5.jpg",
    "https://pbs.twimg.com/media/DlPW9AAW4AAs2O9.jpg:large",
    "https://i.pinimg.com/736x/9b/dc/a0/9bdca0ce9495c9e2fe0d011dd3b6d157.jpg",
    "https://newfastuff.com/wp-content/uploads/2019/06/ZYD2wDy.png",
    "https://i.imgflip.com/4nfm9a.jpg",
    "https://i.imgflip.com/4svgqu.png",
    "https://indianmemetemplates.com/wp-content/uploads/Sick-Spider-man.jpg"
]

#- UTILS
EMBED_COLOR = 0xff0000
BLANK_LINE = '\u200b'
GROUPS_BY_YEAR = {
    3: ['1', '2', '3', '4'],
    4: ['1', '2', '3', '4'],
    5: ['1', '2', '3']
}

# The structure of the timetable website makes it difficult to recover
# the duration of a class slot. The following dictionnary contains the
# main slots in the form {number of colspan => lesson duration in minutes}.
# If the slot is not available here, an algorithm is implemented to determine
# its duration but it does not have 100% accuracy (possible shift of 15 minutes).
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
    20: 240,
    22: 270,
    39: 240,
    49: 360
}
