# multi-victory-prayer-bot
Telegram prayer bot to help you with your Christian walk

# Introduction
This bot can be used for your prayer journey
The idea is to set this up and use this for your personal journeys and count
your victories

The difference between a Full version and a Lite version is the data storage 
strategy. Full version will be a full blown architecture,accommodating for cloud
VM deployments so as to scale for churches. Lite version should store with 
local chat persistence (Using pickle file for now)
For more information you can check these out:
https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent

# How to set this up yourself to develop
## using full version
1. clone/fork this repository or download its binaries
2. change directory to full
3. run the following:
```
touch .env
pip install -r requirements.txt
python main.py
```
## using lite version
1. clone/fork this repository or download its binaries
2. change directory to lite
3. run the following:
```
touch .env
pip install -r requirements.txt
python main.py
```

# How to use this application
Check out the wiki here: https://github.com/joalliswellchin/multi-victory-prayer-bot/wiki 

# How to deploy to cloud
You can deploy to cloud however you like, but it is suggested you put to cloud
for the uptime


# How to contribute
-- this is still work in progress --
You can raise an issue and a pull request (if you found a solution)

# APPENDIX
## Sample env file
```
TELEGRAM_API_KEY=
```
