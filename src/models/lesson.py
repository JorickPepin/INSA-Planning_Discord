from dataclasses import dataclass
from enum import Enum
from datetime import time
from typing import List
from utils import (
    EMOJI_TEACHER, EMOJI_PLACE, EMOJI_LINK,
    YEAR_OF_STUDY, GROUPS_BY_YEAR
)

class LessonType(Enum):
    """Lesson types"""
    CM = ":orange_book:"
    TD = ":blue_book:"
    TP = ":closed_book:"
    SPECIAL = ":mega:"
    SPORT = ":person_running:"
    LANGUAGE = ":speaking_head:"
    PROJECT = ":technologist:"

    def get_emoji(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self.name)


@dataclass
class Lesson:
    """Represent a lesson in the timetable"""
    start_time: time
    end_time: time
    teacher: str
    place: str
    title: str
    type: LessonType
    groups: List[str]
    link: str

    def is_a_group_lesson(self) -> bool:
        """Indicate whether the lesson is common to all groups"""
        return len(self.groups) == len(GROUPS_BY_YEAR[YEAR_OF_STUDY])

    def get_emoji_time(self) -> str:
        """Return the emoji to use for the time according to the start time of the lesson"""

        hour, minutes = self.start_time.hour, self.start_time.minute

        if hour > 12:
            hour -= 12

        if minutes == 30:
            emoji = f":clock{hour}{minutes}:"
        else:
            emoji = f":clock{hour}:"

        return emoji

    def to_string_embed(self) -> List[str]:
        """Prepare and return the name and the value that will be displayed in the embed"""

        name = (
            self.get_emoji_time() +
            f" {self.start_time.strftime('%Hh%M')} - {self.end_time.strftime('%Hh%M')}"
        )

        value = self.type.get_emoji() + " " if self.type else ""

        value += self.title

        if self.type in [LessonType.CM, LessonType.TD, LessonType.TP]:
            value += " [" + self.type.name + "]"

        if self.teacher:
            value += "\n" + EMOJI_TEACHER + " " + self.teacher

        if self.place:
            value += "\n" + EMOJI_PLACE + " " + self.place

        if self.link:
            value += "\n" + EMOJI_LINK + " " + self.link

        return name, value
