import os
import discord
from discord import app_commands
from discord.ext import commands
from cuny_search import DATA_DIR
from typing import Literal, Union


GUILD_ID = discord.Object(id=1358547714341601461)

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f'Synced {len(synced)} commands to guild {GUILD_ID.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

terms = Literal['Spring Term', 'Summer Term', 'Fall Term']
year = app_commands.Range[int, 2025, 2125]
crn = app_commands.Range[int, 1000, 99999]



@client.tree.command(name="check_course_status", description="Checks CUNY Global Search webpage for real-time course status.", guild=GUILD_ID)
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
@app_commands.describe(session="Length of the class. Typically required for Summer or Winter courses.")
@app_commands.describe(session="Name of the college. Usually not required.")
async def check_course_status(
    interaction: discord.Interaction,
    year: app_commands.Range[int, 2025, 2125],
    term: Literal['Spring Term', 'Summer Term', 'Fall Term'],
    course_number: app_commands.Range[int, 0, 999999],
    session: Union[
        None,
        Literal[
            "10 Week",
            "Eight Week - First",
            "Eight Week - Second",
            "Eleven Week",
            "Five Week - First",
            "Five Week - Second",
            "Five Week - Third",
            "Four Week - First",
            "Four Week - Second",
            "Four Week - Third",
            "Less Than 3 Week",
            "Nine Week - First",
            "Nine Week - Second",
            "Regular Academic Session",
            "Second Session",
            "Seven Week - First",
            "Seven Week - Second",
            "Six Week - First",
            "Six Week - Second",
            "Three Week - First",
            "Three Week - Second",
            "Three Week - Third",
            "Twelve Week",
            "Winter"
        ]
    ],
    institution: Union[
        None,
        Literal[
            "Baruch College",
            "Borough of Manhattan CC",
            "Bronx CC",
            "Brooklyn College",
            "City College",
            "College of Staten Island",
            "Graduate Center",
            "Guttman CC",
            "Hostos CC",
            "Hunter College",
            "John Jay College",
            "Kingsborough CC",
            "LaGuardia CC",
            "Lehman College",
            "Medgar Evers College",
            "NYC College of Technology",
            "Queens College",
            "Queensborough CC",
            "School of Journalism",
            "School of Labor&Urban Studies",
            "School of Law",
            "School of Medicine",
            "School of Professional Studies",
            "School of Public Health",
            "York College"
        ]
    ]
):
    message = f"{year} {term}\n Course Number: {course_number}"
    if session:
        message += f"\nSession: {session}"
    if institution:
        message += f"\nInstitution: {institution}"
    await interaction.response.send_message(message)


def start_bot():
    client.run(os.getenv("DISCORD_TOKEN"))