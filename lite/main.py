"""
Data structures:
context.chatdata = {
    "ongoing": {
        "title": [str]
    },
    "fulfilled": {
        "title": [str]
    }
}
context.userdata = {
    "prayer_title": str
}

Other notes:
- Completed prayers are prayers with prayer titles and prayer not blank
- Placing all in one file to make this easier for copy pasta as of now
- Not building prayer titles editing because it should be intended to delete over editing
- Not building 1 prayer title : M prayer, but will consider doing so as it is a valid use case
"""

import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import (filters, MessageHandler, ApplicationBuilder, 
ContextTypes, CommandHandler, PicklePersistence, ConversationHandler)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

# Add prayer, complete prayer, fulfill prayer, edit prayer, delete prayer
TYPING_PRAYER_TITLE, TYPING_PRAYER, NEXT_PRAYER, \
    COMPLETE_PRAYER, \
    SET_FULFILL_PRAYER, \
    ADD_FULFILL_PRAYER, \
    EDIT_PRAYER, \
    DEL_PRAYER = range(8)
# ------------------------------------------------------------------------------
# Display functions
# ------------------------------------------------------------------------------
async def showalluntrackedprayer(update, context):
    """Usage: /showalluntrackedprayer"""
    text = '\n'.join(
        "{}: {}".format(k, v) for k, v in context.chat_data["ongoing"].items()
    )
    if text == '':
        text = 'No prayer requests! Are you slacking?'
    await update.message.reply_text(text)

async def showprayer(update, context):
    """Usage: /showprayer"""
    new_list = context.chat_data["ongoing"].items()
    text = '\n'.join(
        # "{}: {}".format(k, v) for k, v in context.chat_data["ongoing"].items()
        "{}: {}".format(k, v) for k, v in new_list
    )
    if text == '':
        text = 'No prayer requests! Are you slacking?'
    await update.message.reply_text(text)

async def showcompletedprayer(update, context):
    """Usage: /showcompletedprayer"""
    new_list = context.chat_data["ongoing"] #for key, value in context.chat_data["ongoing"]:
    await update.message.reply_text(
        '\n'.join(
            # "{}: {}".format(k, v) for k, v in context.chat_data["ongoing"].items()
            "{}: {}".format(k, v) for k, v in new_list
            )
        )

# TODO: is a repeat of showcompletedprayer, can be made general
async def showvictory(update, context):
    """Usage: /showvictory"""
    await update.message.reply_text(
        '\n'.join(
            "{}: {}".format(k, v) for k, v in context.chat_data["fulfilled"].items()
        )
    )

# ------------------------------------------------------------------------------
# add prayer
# ------------------------------------------------------------------------------
async def input_prayer_title(update, context):
    """Usage: /addprayer"""
    # Generate ID by getting the last number and add 1
    await update.message.reply_text(
        "What is the prayer title?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER_TITLE

async def input_prayer_title_response(update, context):
    if update.message.text in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Prayer title already exists! Edit prayer or delete if you require",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        reply_keyboard = [["Yes", "Not now"]]
        context.user_data["prayer_title"] = update.message.text #store this for continuing
        context.chat_data["ongoing"][update.message.text] = list()
        await update.message.reply_text(
            "Prayer title added. Would you like to continue adding a prayer?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, 
                one_time_keyboard=True, 
                input_field_placeholder="Complete Prayer?"
            ),
        )
        return NEXT_PRAYER

async def completeprayer(update, context):
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER

# ------------------------------------------------------------------------------
# add completed prayer
# ------------------------------------------------------------------------------
# this is to get context if not from addprayer
async def input_completeprayer_title(update, context):
    """Usage: /completeprayer"""
    await update.message.reply_text(
        "What is the prayer title?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return COMPLETE_PRAYER

async def check_input_completeprayer(update, context):
    # uncomment if you only need 1 prayer per prayer title
    # if update.message.text in context.chat_data["ongoing"]:
    #     if context.chat_data["ongoing"][update.message.text]:
    #         await update.message.reply_text(
    #             "There is already a prayer here! Try editing the prayer?",
    #             reply_markup=ReplyKeyboardRemove(),
    #         )
    #         context.user_data.clear()
    #         return ConversationHandler.END
    # else:
    if not update.message.text in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer title! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    # set current user data to hold the message first for append later
    context.user_data["prayer_title"] = update.message.text
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER

# ------------------------------------------------------------------------------
# add fulfilled prayer via complete prayer list
# ------------------------------------------------------------------------------
async def input_fulfillprayer(update, context):
    """Usage: /fulfillprayer"""
    await update.message.reply_text(
        "Which prayer title has been fulfilled?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return SET_FULFILL_PRAYER

async def check_input_fulfillprayer(update, context):
    prayer_title = update.message.text
    if not prayer_title in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer title! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    context.chat_data["fulfilled"][prayer_title] = context.chat_data["ongoing"][prayer_title]
    context.chat_data["ongoing"].pop(prayer_title)
    await update.message.reply_text(
        "Prayer fulfilled! Yay!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


# ------------------------------------------------------------------------------
# add fulfilled prayer directly
# ------------------------------------------------------------------------------
async def input_addfulfillprayer(update, context):
    """Usage: /addfulfillprayer"""
    await update.message.reply_text("")
    return ADD_FULFILL_PRAYER

async def addfulfillprayer(update, context):
    await update.message.reply_text("")

# ------------------------------------------------------------------------------
# edit prayer
# ------------------------------------------------------------------------------
async def input_editprayer(update, context):
    return EDIT_PRAYER

async def editprayer(update, context):
    """Usage: /editprayer key prayer_request_by_user"""
    list_name = "ongoing" # default left as ongoing for now
    prayer_title = context.user_data["prayer_title"]
    value = context.chat_data[list_name].get(prayer_title)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name][prayer_title] = str(update.message.text.split(' ', 2)[-1])
        reply = 'Changes have been saved'
    await update.message.reply_text(reply)

# ------------------------------------------------------------------------------
# delete prayer
# ------------------------------------------------------------------------------
async def input_delprayer(update, context):
    return DEL_PRAYER

async def delprayer(update, context):
    """Usage: /delprayer key"""
    list_name = "ongoing" # default left as ongoing for now
    prayer_title = context.user_data["prayer_title"]
    value = context.chat_data[list_name].get(prayer_title)
    reply = 'Prayer point could not be found'
    if value:
        context.chat_data[list_name].pop(prayer_title)
        reply = 'Deleted prayer'
    await update.message.reply_text(reply)

# ------------------------------------------------------------------------------
# general functions
# ------------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Fix bug where there the conversation is saved and can be viewed in another chat
    # set up data
    context.chat_data["ongoing"] = dict()
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
/editprayer - edit a prayer to the prayer request list at specified prayer title
/delprayer - delete a prayer to the prayer request list at specified prayer title
/completeprayer - you have prayed this, and add prayer to the prayer title
/fulfillprayer - prayers that have been answered
/addfulfillprayer - add answered prayer to prayer list directly
/showprayer - show current prayer list
/showcompletedprayer - show completed prayer list
/showvictory - show fulfilled prayer list
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Sorry, I didn't understand that command."
    )

async def addprayer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    prayer_title = context.user_data["prayer_title"]
    context.chat_data["ongoing"][prayer_title].append(update.message.text)
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

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).build()

    # Create application with pickle file reference and pass it to bot token
    persistence = PicklePersistence(filepath="saved_convo", single_file=False)
    application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).persistence(persistence).build()
    
    # All commands added here
    start_handler = CommandHandler('start', start)
    help_cmd_handler = CommandHandler('help', help)
    showalluntrackedprayer_cmd_handler = CommandHandler('showalluntrackedprayer', showalluntrackedprayer)
    showprayer_cmd_handler = CommandHandler('showprayer', showprayer)
    showcompletedprayer_cmd_handler = CommandHandler('showcompletedprayer', showcompletedprayer)
    showvictory_cmd_handler = CommandHandler('showvictory', showvictory)
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(showalluntrackedprayer_cmd_handler)
    application.add_handler(showprayer_cmd_handler)
    application.add_handler(showcompletedprayer_cmd_handler)
    application.add_handler(showvictory_cmd_handler)
    
    # Allow commands to be also receivable in text
    # help_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addprayer", input_prayer_title)],
        states={
            TYPING_PRAYER_TITLE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    input_prayer_title_response,
                )
            ],
            NEXT_PRAYER: [
                MessageHandler(
                     filters.Regex("^(Yes)$"),
                    completeprayer,
                ),
                MessageHandler(
                     filters.Regex("^(Not now)$"),
                    end_convo,
                )
            ],
            TYPING_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    addprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    complete_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "completeprayer", 
                input_completeprayer_title
            )
        ],
        states={
            COMPLETE_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    check_input_completeprayer,
                )
            ],
            TYPING_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    addprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    #TODO: Complete these flow
    fulfill_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "fulfillprayer", 
                input_fulfillprayer
            )
        ],
        states={
            SET_FULFILL_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    check_input_fulfillprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    addfulfill_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "addfulfillprayer", 
                input_addfulfillprayer
            )
        ],
        states={
            ADD_FULFILL_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    addfulfillprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    editprayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "editprayer", 
                input_editprayer
            )
        ],
        states={
            EDIT_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    editprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    delprayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "delprayer", 
                input_delprayer
            )
        ],
        states={
            DEL_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    application.add_handler(add_conv_handler)
    application.add_handler(complete_conv_handler)
    application.add_handler(fulfill_conv_handler)
    application.add_handler(addfulfill_conv_handler)
    application.add_handler(editprayer_conv_handler)
    application.add_handler(delprayer_conv_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    application.run_polling()