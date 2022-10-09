from datetime import datetime
from dataclasses import dataclass
from typing import List
from .lesson import Lesson

@dataclass
class Timetable:
    """Represent the timetable of a specific day"""

    lessons: List[Lesson]
    date: datetime
    groups: List[str]

    def contains_only_group_lessons(self):
        """Indicate whether all lessons in the timetable are common to all groups"""
        for lesson in self.lessons:
            if lesson.groups != self.groups:
                return False
        return True
