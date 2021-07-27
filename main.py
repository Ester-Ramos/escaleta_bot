from discord.ext import commands
import os
import re
from datetime import date, timedelta, datetime
import textwrap
from parser import Parser

bot = commands.Bot(command_prefix='!')


def get_thursday():
  today = date.today()
  offset = (3 - today.weekday()) % 7
  next_thursday = today + timedelta(days=offset)
  return datetime.strftime(next_thursday, "%d of %B") 

default_message = textwrap.dedent(f"""
  ```asciidoc
  [{get_thursday()}]

  = ACTUALIDAD =
  - Actualidad de los panas

  = NOTICIAS ESPAECIALES = 
 
  = PELIS =

  = SERIES = 

  = JUEGOS =
  
  ```
  """)

def parse_message(message):
    parser = re.compile(".*= (.*?) =\s*(- [^=`]*)*", re.DOTALL)

    parsed_message = {
      section.lower(): [
        element for element in contents.strip().split("\n") if element
      ] for section, contents in parser.findall(message)
    }

    return parsed_message

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


@bot.command(name="tema", help="Elige tema del que quieres hablar")
async def tema(ctx, section, *topic):
    topic = " ".join(topic)
    channel = bot.get_channel(776518954461429811)

    last_message = await channel.fetch_message(channel.last_message_id)
    parsed_message = Parser(last_message.content)
    sections = parsed_message.sections
    sections[section.upper()].append(topic)
    new_message = create_new_message(parsed_message.date, sections)
    await last_message.edit(content=new_message)


@bot.command(name="new", help="Crea un template nuevo para esta semana.")
async def new_week(ctx):
  
    channel = bot.get_channel(776518954461429811)
    await channel.send(default_message)

  
bot.run(os.environ.get('TOKEN'))