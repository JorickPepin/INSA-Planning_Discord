"""
Module containing the discord bot.

Launch the loading of the timetable when the current
time matches the time defined in the .env and create
the discord embed before sending it to the channel.
"""

import random
from datetime import datetime, timedelta
from babel.dates import format_date
from discord import Client, Embed
from discord.ext import tasks
import loader
from models.timetable import Timetable
from utils import (
    DISCORD_TOKEN, DISCORD_CHANNEL_ID,
    REST_IMAGES, LAUNCH_TIME,
    EMOJI_GROUPS, EMBED_COLOR, BLANK_LINE,
    TIME_ZONE, LOCALE, SKIP_WEEKENDS
)

client = Client()

def get_current_time() -> str:
    """Return the current time"""
    return datetime.now(TIME_ZONE).strftime('%H:%M')

def get_tomorrow_date() -> datetime:
    """Return the next day's date"""
    return datetime.now(TIME_ZONE) + timedelta(days=1)

def is_weekend(date: datetime) -> bool:
    """Check if date is a weekend day"""
    return date.isoweekday() in [6,7]

def bold(text: str) -> str:
    """Format a text to be displayed in bold on discord"""
    return "**" + text + "**"

def generate_embed(timetable: Timetable) -> Embed:
    """Generate the discord embed containing the timetable"""

    def create_rest_embed() -> Embed:
        """Create the embed for a day without lesson (rest day)"""

        embed = Embed(title=title, colour=EMBED_COLOR)
        embed.set_image(url=random.choice(REST_IMAGES))

        return embed

    def create_group_embed() -> Embed:
        """Create the embed when all the lessons are common to all groups"""

        embed = Embed(title=title, colour=EMBED_COLOR, description=BLANK_LINE)

        name = "Groupes"
        for group in timetable.groups:
            name += " " + EMOJI_GROUPS.get(group)

        embed.add_field(name=name, value=BLANK_LINE, inline=False)

        for index, lesson in enumerate(timetable.lessons, 1):
            name, value = lesson.to_string_embed()

            if index != len(timetable.lessons): # if it's not the last lesson -> we add one line
                value += "\n" + BLANK_LINE

            embed.add_field(name=name, value=value, inline=False)

        return embed

    def create_embed() -> Embed:
        """Create the embed for a normal day with lessons"""

        embed = Embed(title=title, colour=EMBED_COLOR, description=BLANK_LINE)

        for group in timetable.groups:
            # we sort to recover the lessons concerning this group
            group_lessons = []
            for lesson in timetable.lessons:
                if group in lesson.groups:
                    group_lessons.append(lesson)

            embed.add_field(
                name="Groupe " + EMOJI_GROUPS.get(group),
                value=BLANK_LINE,
                inline=False
            )

            for index, lesson in enumerate(group_lessons, 1):
                name, value = lesson.to_string_embed()

                # if it's not the last lesson of the group -> we add one line
                if index != len(group_lessons):
                    value += "\n" + BLANK_LINE
                # it's the last lesson of the group but it's not the last group -> we add two lines
                elif group != timetable.groups[-1]:
                    value += "\n" + BLANK_LINE + "\n" + BLANK_LINE

                embed.add_field(name=name, value=value, inline=False)

        return embed

    title = bold("Emploi du temps du " + format_date(timetable.date, format='full', locale=LOCALE) + " :") + "\n"

    if not timetable.lessons: # rest day
        return create_rest_embed()

    if timetable.contains_only_group_lessons(): # all the groups have the lessons
        return create_group_embed()

    return create_embed()


@client.event
async def on_ready():
    loop.start()

@tasks.loop(minutes=1)
async def loop():

    if get_current_time() == LAUNCH_TIME:
        tomorrow_date = get_tomorrow_date()
        timetable = loader.get_timetable(tomorrow_date)

        # Skip weekends depends on config
        if not timetable.lessons and SKIP_WEEKENDS and is_weekend(tomorrow_date):
            return

        embed = generate_embed(timetable)
        await client.get_channel(DISCORD_CHANNEL_ID).send(embed=embed)

client.run(DISCORD_TOKEN)
