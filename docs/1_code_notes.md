# Update And Context
Each function when receiving from telegram service will provide 2 inputs:
- Update 
- Context
For more info: https://docs.python-telegram-bot.org/en/v20.6/telegram.ext.commandhandler.html

# Concurrency
As of now, concurrency is built with the ApplicationBuilder
We can consider adding concurrency to handlers later
For more info: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Concurrency