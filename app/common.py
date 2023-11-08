import os
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler


# ------------------------------------------------------------------------------
# general functions
# ------------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /start

    to create all needed data structures and send initial message

    Returns: context.bot.send_message
    """
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
    """
    Usage: /help

    to send a list of commands available

    Returns: context.bot.send_message
    """
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
    """
    Generic message for an unknown command

    Returns: context.bot.send_message
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


async def end_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provide essage when abruptly ending a conversation and clear cache

    Returns: ConversationHandler.END
    """
    # Send message
    await update.message.reply_text(
        "Stopped command! Don't stop praying!",
        reply_markup=ReplyKeyboardRemove(),
    )

    # clear cache
    if "prayer_req" in context.user_data:
        del context.user_data["prayer_req"]
    if "del_prayer_req" in context.user_data:
        del context.user_data["del_prayer_req"]

    return ConversationHandler.END


async def end_request_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provide message when ending a conversation about requests and clear cache

    Returns: ConversationHandler.END
    """
    # Send message
    await update.message.reply_text(
        "Okay! Remember to pray about it!",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Clear cache
    if "prayer_req" in context.user_data:
        del context.user_data["prayer_req"]
    # if "del_prayer_req" in context.user_data:
    #     del context.user_data["del_prayer_req"]

    return ConversationHandler.END


async def addprayer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Add prayer info to request

    Returns: ConversationHandler.END
    """
    prayer_req = context.user_data["prayer_req"]
    now = datetime.now().strftime(os.environ.get("DATETIME_FORMAT"))

    # Add prayer info to chat data
    context.chat_data["ongoing"][prayer_req]["prayers"].append(
        {
            "time": now,
            "prayer": update.message.text,
        }
    )

    # Success message to user
    await update.message.reply_text(
        "Prayer added",  # + context.args[0],
        reply_markup=ReplyKeyboardRemove(),
    )

    # Clear cache
    del context.user_data["prayer_req"]

    return ConversationHandler.END
