import discord
from discord.ext import commands
import os
from datetime import date, timedelta, datetime
import textwrap
from parser import Parser
import requests


r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

activity = discord.Activity(type=discord.ActivityType.listening,
                            name="vuestros temillas")
# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category='Commands',
    width=120,
)

bot = commands.Bot(command_prefix='&',
                   activity=activity,
                   help_command=help_command)

Authors = {
    189850557245030410: "Ester",
    460122607778398208: "Carmen",
    370525554434244609: "Ale",
    512733555772620819: "Jose",
    507975905399013396: "Juan Pablo",
    444561823342002187: "Abraham",
    816342067814072320: "Abraham",
    528941172174094336: "Marta",
}


def get_next_sunday():
    today = date.today()
    offset = (6 - today.weekday()) % 7
    next_sunday = today + timedelta(days=offset)
    return datetime.strftime(next_sunday, "%d of %B")


def create_new_message(date, sections):
    
    parts = ["```asciidoc"]
    parts.append(f"[{date}]")
    parts.append("")
    for section, items in sections.items():
        parts.append(f"= {section} = ")
        parts.append("")
        for item in items:
            parts.append(f"- {item}")
        parts.append("")
    parts.append("```")

    return "\n".join(parts)


@bot.command(
    name="tema",
    help=
    "Elige la seccion y el tema del que vas a hablar.\nSi la seccion tiene espacios ponla entre comillas."
)
async def tema(ctx, section, *topic):
    topic = " ".join(topic)
    channel = bot.get_channel(776518954461429811)

    author = Authors[ctx.message.author.id]

    last_message = await channel.fetch_message(channel.last_message_id)
    parsed_message = Parser(last_message.content)

    if parsed_message.date != get_next_sunday():
        await ctx.send(f"Semana nueva! Creando '{get_next_sunday()}'")
        await new_week(ctx)
        last_message = await channel.fetch_message(channel.last_message_id)
        parsed_message = Parser(last_message.content)

    sections = parsed_message.sections
    if section.upper() not in sections:
        await ctx.send(f"Creando seccion nueva: '{section}'")
        sections[section.upper()] = [f"{topic} ({author})"]
    else:
        sections[section.upper()].append(f"{topic} ({author})")
    new_message = create_new_message(parsed_message.date, sections)
    await last_message.edit(content=new_message)
    await ctx.message.add_reaction("👍")


@bot.command(name="new", help="Crea un template nuevo para esta semana.")
async def new_week(ctx):

    channel = bot.get_channel(776518954461429811)
    await channel.send(
        textwrap.dedent(f"""
    ```asciidoc
    [{get_next_sunday()}]

    = ACTUALIDAD =
    - Actualidad de los panas
 
    = PELIS =

    = SERIES = 

    = JUEGOS =
  
    ```
    """))


@bot.command(name="remove_topic",
             help="Indica el nombre de la seccion y el tema que quieres borrar"
             )
async def remove_topic(ctx, section, *to_remove):
    to_remove = " ".join(to_remove)
    channel = bot.get_channel(776518954461429811)

    last_message = await channel.fetch_message(channel.last_message_id)
    parsed_message = Parser(last_message.content)
    sections = parsed_message.sections
    if section.upper() not in sections:
        await ctx.message.add_reaction("👎")
        await ctx.send(f"La seccion: '{section}' no existe.")
        return

    items = sections[section.upper()]
    sections[section.upper()] = [item for item in items if item != to_remove]
    new_message = create_new_message(parsed_message.date, sections)
    await last_message.edit(content=new_message)
    await ctx.message.add_reaction("👍")


@bot.command(name="remove_section",
             help="Indica la seccion que quieres borrar")
async def remove_section(ctx, section):
    channel = bot.get_channel(776518954461429811)

    last_message = await channel.fetch_message(channel.last_message_id)
    parsed_message = Parser(last_message.content)
    sections = parsed_message.sections
    if section.upper() not in sections:
        await ctx.message.add_reaction("👎")
        await ctx.send(f"La seccion: '{section}' no existe.")
        return

    del sections[section.upper()]
    new_message = create_new_message(parsed_message.date, sections)
    await last_message.edit(content=new_message)
    await ctx.message.add_reaction("👍")


if __name__ == "__main__":
    bot.run(os.environ.get('TOKEN'))
