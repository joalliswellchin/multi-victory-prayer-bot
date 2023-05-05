from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
# ------------------------------------------------------------------------------
# general functions
# ------------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Fix bug where there the conversation is saved and can be viewed in another chat
    # set up data
    if not context.chat_data.get("ongoing"):
        context.chat_data["ongoing"] = dict()
    if not context.chat_data.get("fulfilled"):
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
/request - add a prayer request
/pray - you have prayed this, and add prayer to the prayer request
/answered - prayers that have been answered
/delete - delete a prayer request or prayer
/imanswered - add (immediately) answered prayer to answered prayer list directly
/listall - show the prayer request list
/listrequest - show all prayer requests without prayers
/listpray - show all prayer requests with prayers
/listanswered - show the list of answered prayers
/pickrequest - show the prayer request list to see just the prayers of that prayer request

If you ever need to end the conversation you have with me, just type EXIT (case-sensitive)

Be sure to reply the messages sent by the bot when you are in a group!
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Sorry, I didn't understand that command."
    )

async def end_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the gathered info and end the conversation."""
    await update.message.reply_text(
        "Ending Conversation!",
        reply_markup=ReplyKeyboardRemove(),
    )
    if "prayer_req" in context.user_data:
        del context.user_data["prayer_req"]
    if "del_prayer_req" in context.user_data:
        del context.user_data["del_prayer_req"]
    return ConversationHandler.END

async def end_request_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the gathered info and end the conversation."""
    await update.message.reply_text(
        "Okay! Remember to pray about it!",
        reply_markup=ReplyKeyboardRemove(),
    )
    if "prayer_req" in context.user_data:
        del context.user_data["prayer_req"]
    if "del_prayer_req" in context.user_data:
        del context.user_data["del_prayer_req"]
    return ConversationHandler.END

async def addprayer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    prayer_req = context.user_data["prayer_req"]
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    context.chat_data["ongoing"][prayer_req].append(now + " - " + update.message.text)
    await update.message.reply_text(
        "Prayer added",# + context.args[0],
        reply_markup=ReplyKeyboardRemove(),
    )
    del context.user_data["prayer_req"]
    return ConversationHandler.END