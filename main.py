# import discord
# import os
# import random
# from dotenv import load_dotenv


# load_dotenv()
 
# client = discord.Bot()
# token = os.getenv('TOKEN')


# @client.event
# async def on_ready():
#     print("Logged in as a bot {0.user}".format(client))


# @client.event
# async def on_message(message):
# 	username = str(message.author).split("#")[0]
# 	channel = str(message.channel.name)
# 	user_message = str(message.content)

# 	print(f'Message {user_message} by {username} on {channel}')

# 	if message.author == client.user:
# 		return

# 	if channel == "random":
# 		if user_message.lower() == "hello" or user_message.lower() == "hi":
# 			await message.channel.send(f'Hello {username}')
# 			return
# 		elif user_message.lower() == "bye":
# 			await message.channel.send(f'Bye {username}')
# 		elif user_message.lower() == "tell me a joke":
# 			jokes = [" Can someone please shed more\
# 			light on how my lamp got stolen?",
# 					"Why is she called llene? She\
# 					stands on equal legs.",
# 					"What do you call a gazelle in a \
# 					lions territory? Denzel."]
# 			await message.channel.send(random.choice(jokes))

# client.run(token)

# bot.py
# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

#     fullstring = "StackAbuse"
# substring = "tack"

# if substring in fullstring:
#     print("Found!")
# else:
#     print("Not found!")



    bot_Greeting = 'A meme for you. Ha-ha'
    

    if '#BotMeme' in message.content:
        response = bot_Greeting
        await message.channel.send(response)

client.run(TOKEN)