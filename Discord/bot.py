#%%
from discord.ext import tasks
import discord

from datetime import timedelta, datetime
import psycopg

import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

# get all config from .env file
TOKEN = os.getenv('TOKEN')
DB_NAME = os.getenv('POSTGRES_DB_NAME')
DB_USER = os.getenv('POSTGRES_DB_USER')
DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
DB_HOST = os.getenv('POSTGRES_DB_HOST')
DB_PORT = os.getenv('POSTGRES_DB_PORT')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# load harassment words from words.txt
file_ = open('words.txt', 'r')
file_ = file_.read()
words = file_.split('\n')

muted_sec = 5
muted_limit = 5

@client.event
async def on_ready():
    print('Ready to use')
    await testing.start()


# event loop action when member send message into text channel
@client.event
async def on_message(message):
    if message.guild is not None:
        text = message.content
        author_id = message.author.id
        username = '<@' + str(author_id) + '>'
        text = text.lower()

        if author_id != client.user.id:

            for word in words:
                clean_text = re.sub('[^\u0E00-\u0E7Fa-zA-Z]', "", text)
                m = re.search(word, clean_text)

                if m is not None:

                    # insert data
                    user_id = message.author.id
                    time = datetime.utcnow().replace(microsecond=0)
                    insert_command = """INSERT INTO action (user_id, created_at) VALUES (%s,%s)"""
                    insert_data = (user_id, time)

                    async with await psycopg.AsyncConnection.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT) as aconn:
                        async with aconn.cursor() as cur:
                            get_command = """SELECT * FROM action
                                            WHERE user_id = {}""".format(user_id)
                            await cur.execute(get_command)
                            user_action_records = await cur.fetchall()
                            count = len(user_action_records)
                            count = count + 1

                            if count < muted_limit:
                                role = discord.utils.get(message.author.guild.roles, name='Muted')
                                await message.delete()
                                await message.author.add_roles(role)
                                await message.channel.send('Detect harassment word from {} -> ⚠️ Warning.. You got {} quota left'.format(username, muted_limit-count))

                                time = datetime.utcnow().replace(microsecond=0)
                                insert_command = """INSERT INTO action (user_id, created_at, count) VALUES (%s, %s, %s)"""
                                insert_data = (user_id, time, count)
                                await cur.execute(insert_command, insert_data)

                            else:
                                await message.author.send('You are already banned from the server!!')
                                await message.author.ban()

                                ids = [rec[0] for rec in user_action_records]
                                delete_command = """DELETE FROM action WHERE id IN {}""".format(tuple(ids))
                                await cur.execute(delete_command)

                            await aconn.commit()
                            await cur.close()
                            await aconn.close()

                    break


# loop per 0.5 sec and query database for checking user status
@tasks.loop(seconds = 0.5)
async def testing():
    async with await psycopg.AsyncConnection.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT) as aconn:
        async with aconn.cursor() as cur:
            command = """SELECT * FROM action
                        WHERE is_unmuted = FALSE"""
            await cur.execute(command)
            action_records = await cur.fetchall()

            if action_records:
                for action_record in action_records:
                    start_time = action_record[2]
                    is_unmuted = action_record[3]
                    count = action_record[4]
                    deadline_time = start_time + (count * timedelta(seconds=muted_sec))
                    time = datetime.utcnow().replace(microsecond=0)

                    if (time >= deadline_time) and (is_unmuted == False):
                        id = action_record[0]
                        user_id = action_record[1]
                        user_ = discord.utils.get(client.get_all_members(), id=user_id)
                        role = discord.utils.get(user_.guild.roles, name='Muted')
                        await user_.remove_roles(role)

                        command = """UPDATE action
                                    SET is_unmuted = true
                                    WHERE id = {}""".format(id)

                        await cur.execute(command)
                        await aconn.commit()
            
            await aconn.close()
            await cur.close()


client.run(TOKEN)
# %%
