import discord
from discord.ext import commands
import csv
import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  # Record the message details
  author = message.author.name
  timestamp = message.created_at.strftime('%Y-%m-%d %H:%M')

  # Log the message details
  print(f'Message from {author} at {timestamp}: {message.content}')

  await bot.process_commands(message)


@bot.command()
async def commutelog(ctx):
  # Check if the command is issued in the admin channel
  if ctx.channel.name != 'admin':
    await ctx.send("This command can only be used in the admin channel.")
    return

  # Find the commute-logs channel
  commute_logs_channel = discord.utils.get(ctx.guild.channels,
                                           name='commute-log')

  if not commute_logs_channel:
    await ctx.send("The commute-logs channel was not found.")
    return

  # Generate the filename with the current date and time
  current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
  filename = f"commute_log_{current_datetime}.csv"

  # Create the CSV file and write the header row
  with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Member", "Timestamp", "Message"])

    # Iterate through the messages in the commute-logs channel
    async for message in commute_logs_channel.history(limit=None):
      if message.content.upper() in ["CHECKING IN", "CHECKING OUT"]:
        # Write the message details to the CSV file
        writer.writerow([
          message.author.name,
          message.created_at.strftime('%Y-%m-%d %H:%M'), message.content
        ])

  # Send the CSV file as an attachment in the admin channel
  with open(filename, 'rb') as file:
    await ctx.send(file=discord.File(file, filename=filename))

  # Delete the CSV file
  os.remove(filename)


my_secret = os.environ['token']
bot.run(my_secret)