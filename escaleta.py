import discord
from discord.ext import commands
import os
import re
from datetime import date, timedelta, datetime
import textwrap


def get_thursday():
  today = date.today()
  offset = (today.weekday() - 4) % 7
  next_thursday = today + timedelta(days=offset)
  return datetime.strftime(next_thursday, "%d of %B") 


def parse_message(message, section, tema):
  parser = re.compile(".*= (.*?) =\s*(- [^=`]*)*", re.DOTALL)

  parsed_message = {
    section.lower(): [
      element for element in contents.strip().split("\n") if element
    ] for section, contents in parser.findall(message)
  }
  print(parsed_message)
  
  if parsed_message[section]:
    parsed_message[section].append(f"- {tema}")
  
  else:
    parsed_message[section] = [f"- {tema}"]

  parts =["```asciidoc", f"[{get_thursday()}]"]

  for section, content in parsed_message.items():
    parts.append(f"= {section.upper()} =")
    for element in content:
      parts.append(element)
  
  parts.append("```")
  print('\n'.join(parts))

  return '\n'.join(parts)


bot = commands.Bot(command_prefix='!')


@bot.command(name="juegos", help="Escribe aquí los temas que quieras hablar de juegos.")
async def on_command(ctx):
  command_name, *command_args = ctx.message.content.split()
  
  tema = " ".join(command_args)
  print(tema)
  
  channel = bot.get_channel(776518954461429811)

  try:
    last_message = await channel.fetch_message(channel.last_message_id)
    print(last_message.content)
    await last_message.edit(content=parse_message(last_message.content, command_name[1:].lower(), tema))
  except discord.errors.NotFound:
    await channel.send(textwrap.dedent(f"""
  ```asciidoc
  [{get_thursday()}]

  = ACTUALIDAD =
  - Actualidad de los panas

  = NOTICIAS ESPAECIALES = 
  - 

  = PELIS =
  - 

  = SERIES =
  - 

  = JUEGOS =
  - 
  
  ```
  """))

  
bot.run(os.environ.get('TOKEN'))
