from typing import List

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
