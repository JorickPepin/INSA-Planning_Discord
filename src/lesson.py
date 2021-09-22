from typing import List
from constant import (
    EMOJI_TEACHER, EMOJI_TITLES,
    EMOJI_PLACE, EMOJI_LINK,
    YEAR_OF_STUDY, GROUPS_BY_YEAR
)

class Lesson:
    """Represent a lesson in the planning"""

    def __init__(self, start_time : str, end_time : str, teacher : str, place : str, title : str, type : str, groups : List[str], link : str):
        self.start_time = start_time
        self.end_time = end_time
        self.teacher = teacher
        self.place = place
        self.title = title
        self.type = type
        self.groups = groups
        self.link = link

    def is_a_group_lesson(self) -> bool:
        """Indicates whether the lesson is common to all groups"""

        return len(self.groups) == len(GROUPS_BY_YEAR[YEAR_OF_STUDY])

    def get_emoji_time(self) -> str:
        """Return the emoji to use for the time according to the start time of the lesson"""

        hour, minutes = list(map(int, self.start_time.split('h')))

        if hour > 12:
            hour -= 12

        if minutes == 30:
            emoji = f":clock{hour}{minutes}:"
        else:
            emoji = f":clock{hour}:"

        return emoji

    def to_string_embed(self) -> List[str]:
        """Prepare and return the name and the value that will be displayed in the embed"""

        name = self.get_emoji_time() + f" {self.start_time} - {self.end_time}"

        value = EMOJI_TITLES.get(self.type) + " " if self.type in EMOJI_TITLES else ""

        value += self.title

        if self.type in ['CM', 'TD', 'TP']:
            value += " [" + self.type + "]"

        if self.teacher:
            value += "\n" + EMOJI_TEACHER + " " + self.teacher

        if self.place:
            value += "\n" + EMOJI_PLACE + " " + self.place

        if self.link:
            value += "\n" + EMOJI_LINK + " " + self.link

        return name, value

    def __repr__(self):
        res = f"Time: {self.start_time} - {self.end_time}"

        res += f"\nTitle: {self.title}"

        if self.teacher:
            res += f"\nTeacher: {self.teacher}"

        if self.place:
            res += f"\nPlace: {self.place}"

        if self.type:
            res += f"\nType: {self.type}"

        if self.link:
            res += f"\nLink: {self.link}"

        res += f"\nGroups: {self.groups}"

        return res
