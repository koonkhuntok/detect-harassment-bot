Discord auto detect harassment word bot [Version: Eng & Thai]

# Installation
- Make sure you have python 3.6 ++
- Run command -> pip install requirements.txt
- Run command -> sudo docker-compose up -d
- Run command -> python3 create_table.py
- Edit config in .env file (add TOKEN of your bot in TOKEN variable)
- Run command -> python3 bot.py

# How to setting bot from discord developer
- follow this url: https://www.writebots.com/discord-bot-token/


# Custom
- words.txt file is a blacklist words if you want to add more word you can add in it
- About database if you don't want to use our docker database compose. You can change config in .evn (support only postgresql)