import os
import discord
import random
import subprocess
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
    try:
        # get the current IP address
        ip_address = subprocess.check_output(["hostname", "-I"], text=True)
        netmask = "16"
        gateway = subprocess.check_output("route -n | grep 'UG[ \\t]' | awk '{print $2}'", shell=True, text=True).strip()
        interface = subprocess.check_output("ip route | grep default | awk '{print $5}'", shell=True, text=True).strip()
        print(f"[i] Current IP: {ip_address}")
        print(f"[i] Default gateway: {gateway}")

        while True:
            # generate a random IP address within the network (/16)
            third_octet = random.randint(200,255)
            fourth_octet = random.randint(200,254)
            x = ip_address.split(".")
            x[2] = str(third_octet)
            x[3] = str(fourth_octet)
            new_ip = ".".join(x)

            # check if IP address already exists on the network
            print(f"[i] Checking if {new_ip} exists on the network...")
            ping_results = ping(new_ip, timeout=2, count=3)
            
            results_list = []
            for results in ping_results:
                results_list.append(results.message)

            if (all(i == None for i in results_list)):

                subprocess.run(f"ifconfig eth0 {new_ip}", check=True)
                
                # subprocess.run(['ip', 'addr', 'flush', 'dev', interface], check=True)
                # subprocess.run(['ip', 'addr', 'add', f'{new_ip}/16', 'dev', interface], check=True)
                # subprocess.run(['ip', 'link', 'set', 'up', 'dev', interface], check=True)
                # subprocess.run(['ip', 'route', 'add', 'default', 'via', gateway], check=True)

                print(f"[+] New IP: {new_ip}")
                await ctx.send(f"New IP configured: {new_ip}")
                break
            else:
                print(f"[!] Error! {new_ip} already exists on the network") 
                 

    except Exception as e:
        print(e)
        await ctx.send(f"An error occured: {e}")

    

client.run(TOKEN)
