# this bot is to help test. API key and env is hardcoded here
# bot name is joalliswellchin test bot

import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (filters, MessageHandler, ApplicationBuilder, 
ContextTypes, CommandHandler, PicklePersistence)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def help(update, context):
    help_text = """
Here are the following commands:
/help - prints the list of available commands and what they do
/addprayer - add a prayer to the prayer request list
/editprayer - edit a prayer to the prayer request list at specified list number
/delprayer - delete a prayer to the prayer request list at specified list number
/completeprayer - delete a prayer to the prayer request list at specified list number, and add it to completed list
/showprayer - show current prayer list
/showcompletedprayer - show completed prayer list
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

# TODO: add prompts, and save it in a way where uuid is not used or not visible
async def addprayer(update, context):
    """Usage: /put value"""
    # Generate ID and separate value from command
    key = str(uuid4())
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]

    # Store value
    context.user_data[key] = value
    # Send the key to the user
    await update.message.reply_text(key)

# TODO: add prompts, and save the message based on the index
async def editprayer(update, context):
    """Usage: /get uuid"""
    # TODO: get prayer from prayer list
    # Separate ID from command
    key = context.args[0]
    value = context.user_data.get(key, 'Not found')

    reply = 'Changes have been saved' if value == 'Not found' else 'Prayer point could not be found'
    await update.message.reply_text(reply)

async def showprayer(update, context):
    """Usage: /get uuid"""
    # TODO: get from show prayer list
    await update.message.reply_text('\n'.join(list(context.user_data.values())))

async def showcompletedprayer(update, context):
    """Usage: /get uuid"""
    # TODO: get from show completed prayer list
    await update.message.reply_text('\n'.join(list(context.user_data.values())))

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    # application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).build()

    # Create application with pickle file reference and pass it to bot token
    persistence = PicklePersistence(filepath="saved_convo")
    application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).persistence(persistence).build()
    
    # All commands added here
    start_handler = CommandHandler('start', start)
    help_cmd_handler = CommandHandler('help', help)
    addprayer_cmd_handler = CommandHandler('addprayer', addprayer)
    # editprayer_cmd_handler = CommandHandler('editprayer', editprayer)
    # delprayer_cmd_handler = CommandHandler('delprayer', delprayer)
    # completeprayer_cmd_handler = CommandHandler('completeprayer', completeprayer)
    showprayer_cmd_handler = CommandHandler('showprayer', showprayer)
    showcompletedprayer_cmd_handler = CommandHandler('showcompletedprayer', showcompletedprayer)
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(addprayer_cmd_handler)
    # application.add_handler(editprayer_cmd_handler)
    # application.add_handler(delprayer_cmd_handler)
    # application.add_handler(completeprayer_cmd_handler)
    application.add_handler(showprayer_cmd_handler)
    application.add_handler(showcompletedprayer_cmd_handler)
    
    # Allow commands to be also receivable in text
    help_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)
    addprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), addprayer)
    # editprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), editprayer)
    # delprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), delprayer)
    # completeprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), completeprayer)
    showprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), showprayer)
    showcompletedprayer_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), showcompletedprayer)
    application.add_handler(help_msg_handler)
    application.add_handler(addprayer_msg_handler)
    # application.add_handler(editprayer_msg_handler)
    # application.add_handler(delprayer_msg_handler)
    # application.add_handler(completeprayer_msg_handler)
    application.add_handler(showprayer_msg_handler)
    application.add_handler(showcompletedprayer_msg_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    application.run_polling()