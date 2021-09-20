import re
from datetime import datetime, timedelta, time, date
from typing import List
import requests
from bs4 import BeautifulSoup, element
from pytz import timezone
from lesson import Lesson
from constant import (
    INSA_URL, PLANNING_URL,
    LOGIN, PASSWORD, COLSPAN_DURATION
)

def insa_login() -> None:
    """
    Connects to the INSA server with the user's identifiers.

    The server uses the Central Authentication Service (CAS) system,
    it is necessary to send a first GET request to retrieve the
    login ticket and the execution code before sending a POST one
    with the required information.
    """

    response = session.get(INSA_URL)
    content = BeautifulSoup(response.text, 'lxml')

    execution_code = content.find('input', {'name': 'execution'}).get('value')
    login_ticket = content.find('input', {'name': 'lt'}).get('value')

    form = {
        'username': LOGIN,
        'password': PASSWORD,
        'lt': login_ticket,
        'execution': execution_code,
        '_eventId': 'submit'
    }

    session.post(
        INSA_URL,
        data=form
    )


def determine_desired_date() -> str:
    """
    The date on which we want to retrieve the lessons is the day
    after the date on which the script is launched.

    Output format: dd/mm/yyyy (ex: 16/09/2021)
    """

    time_zone = timezone('Europe/Paris')

    current_date = time_zone.localize(datetime.now())
    tomorrow_date = current_date + timedelta(days=1)

    return tomorrow_date.strftime("%d/%m/%Y")


def load_lessons(desired_date : str) -> List[Lesson]:
    """
    Load the lessons from the desired date of the form dd/mm/yyyy
    thanks to the planning url and the desired year.
    """

    def load_planning() -> str:
        """Send a request to the planning url and return the source code"""

        return session.get(PLANNING_URL).text

    def parse_planning(planning : str):
        """Extract the lessons from the planning"""

        def extract_date(th_tag : element.Tag) -> str:
            """Extract the date from a tag of the form <th rowspan="4">Mardi<br>21/09/2021</th>"""

            return re.search(r'(\d{2}/\d{2}/\d{4})', th_tag.text).group(1)

        def parse_lessons(lessons_to_parse : List[element.Tag]) -> List[Lesson]:
            """Transform the lessons retrieved in the source code into Lesson objects"""

            def parse_lesson(raw_lesson : str, groups : List[str]) -> Lesson:
                """Transform a lesson in the source code into a Lesson object"""

                def clean_title(title : str) -> str:
                    """Clean the lesson title to keep only the necessary information"""

                    return re.search(r'(.*?)( \(| \[)', title).group(1)

                def determine_type(title : str) -> str:
                    """Determine the type of the lesson from its title"""

                    types = {
                        'EDT': 'special',
                        'LV1': 'language',
                        'LV2': 'language',
                        'EPS': 'sport',
                        'CM': 'lecture',
                        'TD': 'TD',
                        'TP': 'TP'
                    }

                    res = None

                    for template, lesson_type in types.items():
                        if template in title:
                            res = lesson_type

                    return res

                def determine_time(time_and_location : re.Match) -> List[str]:
                    """
                    Determine the start time and the end time of a lesson.
                    To determine the end time, the duration of the lesson is needed but
                    it cannot be found explicitly in the source code.
                    """

                    hours, minutes = list(map(int, [time_and_location.group(1), time_and_location.group(2)]))

                    colspan = int(raw_lesson.get('colspan'))

                    duration = COLSPAN_DURATION.get(colspan)

                    if not duration:
                        # if the duration is not in the constant dictionnary, we use the following algorithm which is not 100% accurate

                        # to determine the duration of the lessons, it is necessary to juggle
                        # with the colspans because some are only used as separators

                        colspan_duration = 15 # a colspan corresponds to 15 minutes in the table
                        padding = 0

                        nb_min = hours * 60 + minutes # start time in minutes

                        for i in range(colspan - 1, 1, -1):
                            nb_min += colspan_duration
                            if nb_min % 60 == 0:
                                padding -= 1
                                i -= 1

                        duration = colspan_duration * (colspan + padding)

                    start_time = datetime.combine(date.today(), time(hours, minutes))
                    end_time = start_time + timedelta(hours=duration // 60, minutes=duration % 60)

                    return start_time.strftime('%Hh%M'), end_time.strftime('%Hh%M')


                td_tags = raw_lesson.find_all('td') # the data are stored in <td> tags inside the <tr>

                # time and location
                time_and_location = re.search(r'(\d{2})h(\d{2})(\s@\s(?!-)(.*))?', td_tags[1].text)

                start_time, end_time = determine_time(time_and_location)

                location = time_and_location.group(4) if time_and_location.group(4) else None

                # teacher
                teacher = td_tags[2].text.strip().title()

                # title, link and type
                title_tag = td_tags[0]

                lesson_type = determine_type(title_tag.text)

                link = re.search(r'class="slot-external-link" href="(.*)"', str(title_tag))
                link = link.group(1) if link else None

                title = clean_title(title_tag.text)

                # creation of the Lesson object
                lesson = Lesson(start_time, end_time, teacher, location, title, lesson_type, groups, link)

                return lesson


            lessons = [] # will contain the Lesson objects

            # - global lessons
            # the global lessons are the lessons where all groups are concerned,
            # they are in the <tr> of the group 1 (the <tr> at the index 0)
            global_lessons = lessons_to_parse[0].find_all('td', {'class': ['Slot-CM', 'Slot-EDT', 'Slot-PR']})

            for global_lesson in global_lessons:
                lessons.append(parse_lesson(global_lesson, ['1', '2', '3', '4']))

            # - specific lessons
            for group, tr_tag in enumerate(lessons_to_parse, 1):

                group_lessons = tr_tag.find_all('td', {'class': ['Slot-TD', 'Slot-TP']})

                for group_lesson in group_lessons:
                    lessons.append(parse_lesson(group_lesson, [str(group)]))

            return lessons


        soup_planning = BeautifulSoup(planning, 'lxml')

        raw_lessons = dict() # {date: [<tr> group 1, ..., <tr> group 4]}

        lessons_day = None

        for tr_tag in soup_planning.find_all('tr', {'class': 'hour'}):
            if tr_tag.get('class')[1] == 'row-group-1': # the date is only available in the <tr> of the group 1
                lessons_day = extract_date(tr_tag.find('th'))

                # initialization of a list that will contain the <tr> of each group at the date retrieved
                raw_lessons.setdefault(lessons_day, [])

            raw_lessons[lessons_day].append(tr_tag)

        lessons_to_parse = raw_lessons.get(desired_date) # contains the 4 <tr> in which the lessons of each group are located

        if not lessons_to_parse: # the date is not in the planning
            raise KeyError(f"There are no lessons on {desired_date}")

        return parse_lessons(lessons_to_parse)


    planning = load_planning()
    lessons = parse_planning(planning)

    return lessons


def main():
    """Program launch"""

    insa_login()

    desired_date = determine_desired_date()
    lessons = load_lessons(desired_date)
    for lesson in lessons:
        print(lesson)
        print('--------')


if __name__ == '__main__':
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    main()
