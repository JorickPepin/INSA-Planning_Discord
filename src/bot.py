import random
from discord import Client, Embed
from discord.ext import tasks
from datetime import date, datetime, timedelta
from typing import List
import loader
from lesson import Lesson
from constant import (
    REST_IMAGES, GROUPS_BY_YEAR, YEAR_OF_STUDY,
    DISCORD_TOKEN, DISCORD_CHANNEL_ID, LAUNCH_TIME,
    EMOJI_GROUPS, EMBED_COLOR, BLANK_LINE
)

client = Client()

def get_hour():
    """Return the current time"""
    return datetime.today().strftime('%Hh%M')

def determine_desired_date() -> datetime:
    """
    Return the date on which we want to retrieve the lessons,
    i.e. the day after the date on which the script is launched.
    """

    tomorrow_date = datetime.today() + timedelta(days=1)

    return tomorrow_date

def bold(text : str) -> str:
    """Format a text to be displayed in bold on discord"""
    return "**" + text + "**"

def generate_embed(lessons : List[Lesson], desired_date : datetime) -> str:
    """Generate the embed to display in the channel"""

    def create_rest_embed(title : str) -> Embed:
        """Create the embed for a day without lesson (rest day)"""

        embed = Embed(title=title, colour=EMBED_COLOR) 
        embed.set_image(url=random.choice(REST_IMAGES))

        return embed

    def create_group_embed(lessons : List[Lesson], title : str) -> Embed:
        """Create the embed when all the lessons are common to all groups"""

        embed = Embed(title=title, colour=EMBED_COLOR, description=BLANK_LINE)

        name = "Groupes"
        for group in GROUPS_BY_YEAR[YEAR_OF_STUDY]:
            name += " " + EMOJI_GROUPS.get(group)

        embed.add_field(name=name, value=BLANK_LINE, inline=False)
        
        for index, lesson in enumerate(lessons, 1):
            name, value = lesson.to_string_embed()

            if index != len(lessons): # if it's not the last lesson -> we add one line
                value += "\n" + BLANK_LINE

            embed.add_field(name=name, value=value, inline=False)

        return embed

    def create_embed(lessons : List[Lesson], title : str) -> Embed:
        """Create the embed for a normal day with lessons"""

        embed = Embed(title=title, colour=EMBED_COLOR, description=BLANK_LINE) 

        for group in GROUPS_BY_YEAR[YEAR_OF_STUDY]:

            # we sort to recover the lessons concerning this group
            group_lessons = []
            for lesson in lessons:
                if group in lesson.groups:
                    group_lessons.append(lesson)

            embed.add_field(name="Groupe " + EMOJI_GROUPS.get(group), value=BLANK_LINE, inline=False)

            for index, lesson in enumerate(group_lessons, 1):
                name, value = lesson.to_string_embed()

                if index != len(group_lessons): # if it's not the last lesson of the group -> we add one line
                    value += "\n" + BLANK_LINE
                elif group != GROUPS_BY_YEAR[YEAR_OF_STUDY][-1]: # it's the last lesson of the group but it's not the last group -> we add two lines
                    value += "\n" + BLANK_LINE + "\n" + BLANK_LINE

                embed.add_field(name=name, value=value, inline=False)
        
        return embed

    title = bold("Emploi du temps du " + desired_date.strftime("%A %d %B") + " :") + "\n"

    if not lessons: # rest day
        return create_rest_embed(title)

    only_group_lessons = True
    for lesson in lessons:
        if not lesson.is_a_group_lesson():
            only_group_lessons = False
            break

    if only_group_lessons: # all the groups have the lessons
        return create_group_embed(lessons, title)

    return create_embed(lessons, title)

@client.event
async def on_ready():
    loop.start() 

@tasks.loop(minutes=1)
async def loop():

    if get_hour() == LAUNCH_TIME:
        desired_date = determine_desired_date()

        lessons = loader.get_lessons(desired_date)

        embed = generate_embed(lessons, desired_date)

        await client.get_channel(DISCORD_CHANNEL_ID).send(embed=embed)

    
client.run(DISCORD_TOKEN)
 