import re
from datetime import datetime, timedelta, time, date
from typing import List, Optional
from requests import Session
from bs4 import BeautifulSoup, element
from models.lesson import Lesson
from models.timetable import Timetable
from utils import (
    INSA_URL, TIMETABLE_URL,
    LOGIN, PASSWORD, COLSPAN_DURATION,
    GROUPS_BY_YEAR, YEAR_OF_STUDY,
    LessonType
)


def insa_login() -> Session:
    """
    Connect to the INSA server with the user's identifiers and return the created session.

    The server uses the Central Authentication Service (CAS) system,
    it is necessary to send a first GET request to retrieve the
    login ticket and the execution code before sending a POST one
    with the required information.
    """
    session = Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

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

    return session


def load_lessons(session: Session, desired_date: datetime) -> List[Lesson]:
    """Load the lessons for the desired date"""

    def get_timetable_source_code() -> str:
        """Send a request to the timetable url and return the source code"""
        return session.get(TIMETABLE_URL).text

    def parse_timetable(timetable_source_code: str) -> List[Lesson]:
        """Extract the lessons from the timetable source code"""

        def extract_date(th_tag: element.Tag) -> str:
            """Extract the date from a tag of the form <th rowspan="4">Mardi<br>21/09/2021</th>"""
            return re.search(r'(\d{2}/\d{2}/\d{4})', th_tag.text).group(1)

        def parse_lessons(lessons_to_parse: List[element.Tag]) -> List[Lesson]:
            """Transform the lessons retrieved in the source code into Lesson objects"""

            def parse_lesson(raw_lesson: str, groups: List[str]) -> Lesson:
                """Transform a lesson in the source code into a Lesson object"""

                def clean_title(title: str) -> str:
                    """Clean the lesson title to keep only the necessary information"""
                    return re.search(r'(.*?)( \((LV1|LV2|EPS)| \[)', title).group(1)

                def determine_type(title: str) -> Optional[LessonType]:
                    """Determine the type of the lesson from its title"""
                    types = {
                        'EDT': LessonType.SPECIAL,
                        'LV1': LessonType.LANGUAGE,
                        'LV2': LessonType.LANGUAGE,
                        'EPS': LessonType.SPORT,
                        'PR': LessonType.PROJECT,
                        'CM': LessonType.CM,
                        'TD': LessonType.TD,
                        'TP': LessonType.TP
                    }

                    for template, lesson_type in types.items():
                        if template in title:
                            return lesson_type
                    return None

                def determine_end_time(start_time: time) -> time:
                    """
                    To determine the end time, the duration of the lesson is needed but
                    it cannot be found explicitly in the source code.
                    """

                    colspan = int(raw_lesson.get('colspan'))

                    duration = COLSPAN_DURATION.get(colspan)

                    if not duration:
                        # if the duration is not in the constant dictionnary, we use the following
                        # algorithm which is not 100% accurate

                        # to determine the duration of the lessons, it is necessary to juggle
                        # with the colspans because some are only used as separators

                        colspan_duration = 15 # a colspan corresponds to 15 minutes in the table
                        padding = 0

                        nb_min = start_time.hour * 60 + start_time.minute # start time in minutes

                        for i in range(colspan - 1, 1, -1):
                            nb_min += colspan_duration
                            if nb_min % 60 == 0:
                                padding -= 1
                                i -= 1

                        duration = colspan_duration * (colspan + padding)

                    end_time = ( # end time = start time + duration
                        datetime.combine(date.today(), start_time)
                        + timedelta(hours=duration // 60, minutes=duration % 60)
                    )

                    return end_time.time()

                # the data are stored in <td> tags inside the <tr>
                td_tags = raw_lesson.find_all('td')

                # time and location
                time_and_location = re.findall(
                    r'(\d{2}h\d{2})(?:\s@\s(?!-)(.*))? ',
                    td_tags[1].text
                )[0]

                hour, minute = map(int, time_and_location[0].split('h'))
                start_time = time(hour, minute)
                end_time = determine_end_time(start_time)

                location = time_and_location[1] if time_and_location[1] else None

                # teacher
                teacher = td_tags[2].text.strip().title()

                # title, link and type
                title_tag = td_tags[0]

                lesson_type = determine_type(title_tag.text)

                link = re.search(r'class="slot-external-link" href="(.*)"', str(title_tag))
                link = link.group(1) if link else None

                title = clean_title(title_tag.text)

                # creation of the Lesson object
                return Lesson(
                    start_time, end_time, teacher, location,
                    title, lesson_type, groups, link
                )

            lessons = [] # will contain the Lesson objects

            # - global lessons
            # the global lessons are the lessons where all groups are concerned,
            # they are in the <tr> of the group 1 (the <tr> at the index 0)
            global_lessons = lessons_to_parse[0].find_all(
                'td',
                {'class': ['Slot-CM', 'Slot-EDT', 'Slot-PR']}
            )

            for global_lesson in global_lessons:
                lessons.append(parse_lesson(global_lesson, GROUPS_BY_YEAR[YEAR_OF_STUDY]))

            # - specific lessons
            for group, tr_tag in enumerate(lessons_to_parse, 1):
                group_lessons = tr_tag.find_all('td', {'class': ['Slot-TD', 'Slot-TP']})

                for group_lesson in group_lessons:
                    lessons.append(parse_lesson(group_lesson, [str(group)]))

            return lessons


        soup_timetable = BeautifulSoup(timetable_source_code, 'lxml')

        raw_lessons = dict() # {date: [<tr> group 1, ..., <tr> group 4]}

        lessons_day = None

        for tr_tag in soup_timetable.find_all('tr', {'class': 'hour'}):
            # the date is only available in the <tr> of the group 1
            if tr_tag.get('class')[1] == 'row-group-1':
                lessons_day = extract_date(tr_tag.find('th'))

                # init a list that will contain the <tr> of each group at the date retrieved
                raw_lessons.setdefault(lessons_day, [])

            raw_lessons[lessons_day].append(tr_tag)

        desired_date_formatted = desired_date.strftime("%d/%m/%Y")

        # contains the 4 <tr> in which the lessons of each group are located
        lessons_to_parse = raw_lessons.get(desired_date_formatted)

        if not lessons_to_parse: # the date is not in the timetable
            return None

        return parse_lessons(lessons_to_parse)


    timetable_source_code = get_timetable_source_code()
    lessons = parse_timetable(timetable_source_code)

    return lessons


def get_timetable(desired_date: datetime) -> Timetable:
    """
    Launch the recovery of the lessons and return the
    timetable containing them.
    """

    session = insa_login()
    lessons = load_lessons(session, desired_date)
    session.close()

    return Timetable(lessons=lessons, date=desired_date)
