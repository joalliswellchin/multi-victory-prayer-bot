"""
Data structures:
context.chatdata = {
    "ongoing": {
        "title": str
    },
    "complete": {
        "title": str
    },
    "fulfilled": {
        "title": str
    }
}
context.userdata = {
    "prayer_title": str
}
"""

import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (filters, MessageHandler, ApplicationBuilder, 
ContextTypes, CommandHandler, PicklePersistence, ConversationHandler)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Fix bug where there the conversation is saved and can be viewed in another chat
    # set up data
    context.chat_data["ongoing"] = dict()
    context.chat_data["complete"] = dict()
    context.chat_data["fulfilled"] = dict()
    intro = """
Hi Prayer Warrior! Welcome to the MVP bot!

This bot is aimed to improve your prayer walk!
Hit /help if it is your first time here to get to know me!
"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=intro)

async def help(update, context):
    help_text = """
Here are the following commands:
/help - prints the list of available commands and what they do
/addprayer - add a prayer to the prayer request list
/editprayer - edit a prayer to the prayer request list at specified list number
/delprayer - delete a prayer to the prayer request list at specified list number
/completeprayer - you have prayed this, and add this to completed list
/fulfillprayer - prayers that have been answered
/addfulfillprayer - add answered prayer to prayer list directly
/showprayer - show current prayer list
/showcompletedprayer - show completed prayer list
/showcompletedprayer - show fulfilled prayer list
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

# TODO: add prompts, and save the message based on the index
async def editprayer(update, context):
    """Usage: /editprayer key prayer_request_by_user"""
    list_name = "ongoing" # default left as ongoing for now
    key = context.args[0]
    value = context.chat_data[list_name].get(key)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name][key] = str(update.message.text.split(' ', 2)[-1])
        reply = 'Changes have been saved'
    await update.message.reply_text(reply)

# TODO: add prompts
async def delprayer(update, context):
    """Usage: /delprayer key"""
    list_name = "ongoing" # default left as ongoing for now
    key = context.args[0]
    value = context.chat_data[list_name].get(key)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name].pop(key)
        reply = 'Deleted prayer'
    await update.message.reply_text(reply)

# TODO: add prompts
async def completeprayer(update, context):
    """Usage: /completeprayer key"""
    list_name = "ongoing" # default left as ongoing for now
    key = context.args[0]
    value = context.chat_data[list_name].get(key)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name].pop(key)
        context.chat_data["complete"][key] = value # TODO: calculate numeric key here
        reply = 'Yay! You have completed this prayer!'
    await update.message.reply_text(reply)

# TODO: add prompts
# TODO: is a repeat of completeprayer, can be made general
async def fulfillprayer(update, context):
    """Usage: /fulfillprayer key"""
    list_name = "complete" # default left as ongoing for now
    key = context.args[0]
    value = context.chat_data[list_name].get(key)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name].pop(key)
        context.chat_data["fulfilled"][key] = value # TODO: calculate numeric key here
        reply = 'Yay! You have completed this prayer!'
    await update.message.reply_text(reply)

# TODO: add prompts, and save it in a way where uuid is not used or not visible
async def addfulfillprayer(update, context):
    """Usage: /addfulfillprayer prayer_request_by_user"""
    # Generate ID by getting the last number and add 1
    key = str(uuid4()) 
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]

    # Store value
    context.chat_data["fulfilled"][key] = value
    # Send the key to the user
    await update.message.reply_text(key)

async def showprayer(update, context):
    """Usage: /showprayer"""
    text = '\n'.join(list(context.chat_data["ongoing"].values()))
    if text == '':
        text = 'No prayer requests! Are you slacking?'
    await update.message.reply_text(text)

async def showcompletedprayer(update, context):
    """Usage: /showcompletedprayer"""
    await update.message.reply_text('\n'.join(list(context.chat_data["complete"].values())))

# TODO: is a repeat of showcompletedprayer, can be made general
async def showvictory(update, context):
    """Usage: /showvictory"""
    await update.message.reply_text('\n'.join(list(context.chat_data["fulfilled"].values())))

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

TYPING_PRAYER_TITLE, TYPING_PRAYER = range(2)

async def get_prayer_title(update, context):
    """Usage: /addprayer prayer_request_by_user"""
    # Generate ID by getting the last number and add 1
    await update.message.reply_text(
        "What is the prayer title?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER_TITLE

async def get_prayer(update, context):
    context.user_data["prayer_title"] = update.message.text
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER

async def addprayer(update, context):
    prayer_title = context.user_data["prayer_title"]
    context.chat_data["ongoing"][prayer_title] = update.message.text
    await update.message.reply_text(
        "Prayer added",# + context.args[0],
        reply_markup=ReplyKeyboardRemove(),
    )
    del context.user_data["prayer_title"]
    return ConversationHandler.END

async def end_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the gathered info and end the conversation."""
    await update.message.reply_text(
        "Ending Conversation!",
        reply_markup=ReplyKeyboardRemove(),
    )
    if "prayer_title" in context.user_data:
        del context.user_data["prayer_title"]
    return ConversationHandler.END

if __name__ == '__main__':
    # application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).build()

    # Create application with pickle file reference and pass it to bot token
    persistence = PicklePersistence(filepath="saved_convo", single_file=False)
    application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).persistence(persistence).build()
    
    # All commands added here
    start_handler = CommandHandler('start', start)
    help_cmd_handler = CommandHandler('help', help)
    editprayer_cmd_handler = CommandHandler('editprayer', editprayer)
    delprayer_cmd_handler = CommandHandler('delprayer', delprayer)
    completeprayer_cmd_handler = CommandHandler('completeprayer', completeprayer)
    fulfillprayer_cmd_handler = CommandHandler('fulfillprayer', fulfillprayer)
    addfulfillprayer_cmd_handler = CommandHandler('addfulfillprayer', addfulfillprayer)
    showprayer_cmd_handler = CommandHandler('showprayer', showprayer)
    showcompletedprayer_cmd_handler = CommandHandler('showcompletedprayer', showcompletedprayer)
    showvictory_cmd_handler = CommandHandler('showvictory', showvictory)
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(editprayer_cmd_handler)
    application.add_handler(delprayer_cmd_handler)
    application.add_handler(completeprayer_cmd_handler)
    application.add_handler(fulfillprayer_cmd_handler)
    application.add_handler(addfulfillprayer_cmd_handler)
    application.add_handler(showprayer_cmd_handler)
    application.add_handler(showcompletedprayer_cmd_handler)
    application.add_handler(showvictory_cmd_handler)
    
    # Allow commands to be also receivable in text
    # help_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)
    addprayer_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addprayer", get_prayer_title)],
        states={
            TYPING_PRAYER_TITLE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    get_prayer,
                )
            ],
            TYPING_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    addprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), end_convo)],
    )
    application.add_handler(addprayer_conv_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    application.run_polling()