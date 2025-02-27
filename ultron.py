import os
import discord
import random
import subprocess
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from pythonping import ping

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.command()
async def configure(ctx):
    await ctx.send("Hello!")

@client.command()
async def rotateip(ctx):
    await ctx.send("Changing IP address, give me a minute or so.")

    channel_id = ctx.channel.id
    try:
        subprocess.Popen(["python3", "change_ip_and_restart.py", str(channel_id)]) 
        await client.close()
    except Exception as e:
        print(e)
        await ctx.send(f"An error occurred: {e}")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
    # Check if we just changed IP by looking for our info file
    if os.path.exists("ip_change_info.txt"):
        try:
            with open("ip_change_info.txt", "r") as f:
                lines = f.readlines()
                channel_id = int(lines[0].strip())
                new_ip = lines[1].strip()
            
            # Send confirmation to the original channel
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(f"IP change complete! New IP: {new_ip}")
            
            # Clean up the file
            os.remove("ip_change_info.txt")
        except Exception as e:
            print(f"Error during reconnection notification: {e}")

client.run(TOKEN)
