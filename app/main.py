"""
Data structures:
context.chatdata = {
    "ongoing": {
        "req": [str]
    },
    "fulfilled": {
        "req": [str]
    }
}
context.userdata = {
    "prayer_req": str
}

Other notes:
- Completed prayers are prayers with prayer requests and prayer not blank
- Placing all in one file to make this easier for copy pasta as of now (and other architecture mini-concerns)
- Not building prayer requests editing because it should be intended to delete over editing
- context.userdata is only for temporary data within a conversation
"""

from datetime import datetime
import logging
import os

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (filters, MessageHandler, ApplicationBuilder, 
ContextTypes, CommandHandler, PicklePersistence, ConversationHandler, 
CallbackQueryHandler)

from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv(os.path.dirname(os.path.realpath(__file__)) + "/.env")

# Add prayer, complete prayer, fulfill prayer, edit prayer, delete prayer
TYPING_PRAYER_REQ, TYPING_PRAYER, NEXT_PRAYER, \
    COMPLETE_PRAYER, \
    FULFILL_PRAYER, \
    ADD_FULFILL_PRAYER, SET_FULFILL_PRAYER, \
    CHOOSE_DEL_PRAYER, TYPING_DEL_PRAYER_PRAYERREQ, TYPING_DEL_PRAYER_REQ, \
    TYPING_DEL_PRAYER_INDEX = range(11)
# ------------------------------------------------------------------------------
# Display functions
# ------------------------------------------------------------------------------
async def showunprayed(update, context):
    """
    Usage: /showunprayed
    Show all untracked prayer (ongoing and value == "")
    """
    untracked = {k:v for k,v in context.chat_data["ongoing"].items() if not v}
    text = '\n\n'.join(
        "<b>{}</b>".format(k) for k, _ in untracked.items()
    )
    if text == '':
        text = 'No prayer requests! Are you slacking?'
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def showprayerrequest(update, context):
    """
    Usage: /showprayerrequest
    """
    if len(context.chat_data["ongoing"].items()) == 0:
        await update.message.reply_text('No prayer requests! Are you slacking?')
        return ConversationHandler.END
    # TODO: fix inline keyboard to have multiple rows
    all_items = [InlineKeyboardButton(k, callback_data=k) for k,_ in context.chat_data["ongoing"].items()]
    inline_keyboard = list()
    row = list()
    item_per_row = 3
    for index, item in enumerate(all_items):
        row.append(item)
        if index % item_per_row == item_per_row - 1:
            inline_keyboard.append(row)
            row = list()
    if len(row) > 0:
        inline_keyboard.append(row)
    # inline_keyboard = [[InlineKeyboardButton(k, callback_data=k) for k,_ in context.chat_data["ongoing"].items()]]
    await update.message.reply_text(
        "Which prayer request you want to show?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard
        ),
    )

async def showprayerrequest_prayers(update, context):
    """
    Shows prayers of prayer request
    """
    query = update.callback_query
    await query.answer()
    prayer_list = context.chat_data["ongoing"][query.data]
    v_list = ""
    for index, prayer_v in enumerate(prayer_list):
        v_list += "{}: {}\n".format(index + 1, prayer_v)
    if v_list == "":
        v_list = "No prayers yet"
    await query.edit_message_text(query.data)
    await update.effective_chat.send_message(v_list)

async def showall(update, context):
    """
    Usage: /showall
    Show all prayer (untracked and completed)
    """
    new_list = context.chat_data["ongoing"].items()
    reply = ""
    for k, v in new_list:
        v_list = "\n"
        if len(v) == 0:
            v_list += "<i>Not prayed yet</i>\n"
        for index, prayer_v in enumerate(v):
            v_list += "{}: {}\n".format(index + 1, prayer_v)
        reply += "<b>{}</b> {}\n".format(k, v_list)
    # reply = '\n'.join(
    #     # "{}: {}".format(k, v) for k, v in context.chat_data["ongoing"].items()
    #     "{}: {}".format(k, v) for k, v in new_list
    # )
    if reply == '':
        reply = 'No prayer requests! Are you slacking?'
    await update.message.reply_text(reply, parse_mode=ParseMode.HTML)

async def showprayed(update, context):
    """
    Usage: /showprayed
    Show all completed prayer (ongoing and value that is not empty)
    """
    completed = {k:v for k,v in context.chat_data["ongoing"].items() if v}
    reply = ""
    for k, v in completed.items():
        v_list = "\n"
        for index, prayer_v in enumerate(v):
            v_list += "{}: {}\n".format(index + 1, prayer_v)
        reply += "<b>{}</b> {}\n".format(k, v_list)
    # reply = '\n'.join(
    #     # "{}: {}".format(k, v) for k, v in context.chat_data["ongoing"].items()
    #     "{}: {}".format(k, v) for k, v in completed.items()
    # )
    await update.message.reply_text(reply, parse_mode=ParseMode.HTML)

async def showvictory(update, context):
    """Usage: /showvictory"""
    reply = ""
    for k, v in context.chat_data["fulfilled"].items():
        v_list = "\n"
        for index, prayer_v in enumerate(v):
            v_list += "{}: {}\n".format(index + 1, prayer_v)
        reply += "<b>{}</b> {}\n".format(k, v_list)
    await update.message.reply_text(
        reply, 
        parse_mode=ParseMode.HTML,
        # '\n'.join(
        #     "{}: {}".format(k, v) for k, v in context.chat_data["fulfilled"].items()
        # )
    )

# ------------------------------------------------------------------------------
# add prayer
# ------------------------------------------------------------------------------
async def input_prayer_req(update, context):
    """Usage: /addprayer"""
    # Generate ID by getting the last number and add 1
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER_REQ

async def check_input_prayer_req(update, context):
    if update.message.text in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Prayer request already exists! Edit prayer or delete if you require",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        reply_keyboard = [["Yes", "Not now"]]
        context.user_data["prayer_req"] = update.message.text #store this for continuing
        context.chat_data["ongoing"][update.message.text] = list()
        await update.message.reply_text(
            "Prayer request added. Would you like to continue adding a prayer?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, 
                one_time_keyboard=True, 
                input_field_placeholder="Complete Prayer?"
            ),
        )
        return NEXT_PRAYER

async def complete_prayer_req(update, context):
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_PRAYER

# ------------------------------------------------------------------------------
# add completed prayer
# ------------------------------------------------------------------------------
# this is to get context if not from addprayer
async def input_complete_prayer_req(update, context):
    """Usage: /complete_prayer_req"""
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return COMPLETE_PRAYER

async def check_complete_prayer_req(update, context):
    # uncomment if you only need 1 prayer per prayer request
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
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    # set current user data to hold the message first for append later
    context.user_data["prayer_req"] = update.message.text
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
        "Which prayer request has been fulfilled?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FULFILL_PRAYER

async def check_input_fulfillprayer(update, context):
    prayer_req = update.message.text
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    context.chat_data["fulfilled"][now + " - " + prayer_req] = context.chat_data["ongoing"][prayer_req]
    context.chat_data["ongoing"].pop(prayer_req)
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
    await update.message.reply_text("What is the prayer that was answered?")
    return ADD_FULFILL_PRAYER

async def addfulfillprayer(update, context):
    answered_prayer = update.message.text
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    context.chat_data["fulfilled"][now + " - " + answered_prayer] = list()
    await update.message.reply_text("Added answered prayer!")

# ------------------------------------------------------------------------------
# edit prayer
# ------------------------------------------------------------------------------
# TODO: COMMENTING THIS PART OUT AS EDITING IS MORE COMPLEX
# TO EDIT, DELETE THEN ADD AGAIN
# async def input_editprayer(update, context):
#     return EDIT_PRAYER

# async def editprayer(update, context):
#     """Usage: /editprayer key prayer_request_by_user"""
#     list_name = "ongoing" # default left as ongoing for now
#     prayer_req = context.user_data["prayer_req"]
#     value = context.chat_data[list_name].get(prayer_req)
#     reply = 'Prayer point could not be found'
#     if value:
#         context.chat_data[list_name][prayer_req] = str(update.message.text.split(' ', 2)[-1])
#         reply = 'Changes have been saved'
#     await update.message.reply_text(reply)

# ------------------------------------------------------------------------------
# delete prayer
# ------------------------------------------------------------------------------
async def choose_delprayer_mode(update, context):
    reply_keyboard = [["Delete Prayer Request", "Delete Prayer in Prayer Request"]]
    await update.message.reply_text(
        "Do you want to remove a prayer request or prayer in a prayer request?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            input_field_placeholder="Delete prayer or request?"
        ),
    )
    return CHOOSE_DEL_PRAYER

# delete prayer in prayer req
async def input_del_prayerreq(update, context):
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_DEL_PRAYER_REQ

async def del_prayer_req(update, context):
    prayer_req = update.message.text
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    context.chat_data["ongoing"].pop(prayer_req)
    await update.message.reply_text(
        "Prayer request deleted!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END

# delete prayer req
async def input_delprayer_prayerreq(update, context):
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_DEL_PRAYER_PRAYERREQ

async def input_delprayer(update, context):
    prayer_req = update.message.text
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    elif len(context.chat_data["ongoing"][prayer_req]) == 0:
        await update.message.reply_text(
            "Prayer request has no prayers!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    await update.message.reply_text(
        "Which prayer is it? Please provide the number",
        reply_markup=ReplyKeyboardRemove(),
    )
    # TODO: display this
    reply = ""
    for index, value in enumerate(context.chat_data["ongoing"][prayer_req]):
        reply += "{}: {}\n".format(index + 1, value)
    if not reply == "":
        await update.message.reply_text(
            reply,
            reply_markup=ReplyKeyboardRemove(),
        )
    context.user_data["del_prayer_req"] = update.message.text #store this for continuing
    return TYPING_DEL_PRAYER_INDEX

async def delprayer(update, context):
    """Usage: /delprayer key"""
    # because actual numbers start from 1, we deduct the index to start from 0
    index = int(update.message.text) - 1
    if index >= len(context.chat_data["ongoing"][context.user_data["del_prayer_req"]]):
        await update.message.reply_text(
            "Option not available!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    del context.chat_data["ongoing"][context.user_data["del_prayer_req"]][index]
    await update.message.reply_text(
        "Deleted prayer point!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END

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

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).build()

    # Create application with pickle file reference and pass it to bot token
    persistence = PicklePersistence(
        filepath=os.path.dirname(os.path.realpath(__file__)) + "/assets/saved_convo", 
        single_file=False,
    )
    application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).persistence(persistence).build()
    
    # All commands added here
    start_handler = CommandHandler('start', start)
    help_cmd_handler = CommandHandler('help', help)
    showunprayed_cmd_handler = CommandHandler('listrequest', showunprayed)
    showprayerrequest_cmd_handler = CommandHandler('pickrequest', showprayerrequest)
    showall_cmd_handler = CommandHandler('listall', showall)
    showprayed_cmd_handler = CommandHandler('listpray', showprayed)
    showvictory_cmd_handler = CommandHandler('listanswered', showvictory)
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(showunprayed_cmd_handler)
    application.add_handler(showprayerrequest_cmd_handler)
    application.add_handler(CallbackQueryHandler(showprayerrequest_prayers))
    application.add_handler(showall_cmd_handler)
    application.add_handler(showprayed_cmd_handler)
    application.add_handler(showvictory_cmd_handler)
    
    # Allow commands to be also receivable in text
    # help_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)
    prayerreq_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("request", input_prayer_req)],
        states={
            TYPING_PRAYER_REQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    check_input_prayer_req,
                )
            ],
            NEXT_PRAYER: [
                MessageHandler(
                     filters.Regex("^(Yes)$"),
                    complete_prayer_req,
                ),
                MessageHandler(
                     filters.Regex("^(Not now)$"),
                    end_request_convo,
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
    prayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "pray", 
                input_complete_prayer_req
            )
        ],
        states={
            COMPLETE_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    check_complete_prayer_req,
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
                "answered", 
                input_fulfillprayer
            )
        ],
        states={
            FULFILL_PRAYER: [
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
                "imanswered", 
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
    # editprayer_conv_handler = ConversationHandler(
    #     entry_points=[
    #         CommandHandler(
    #             "editprayer", 
    #             input_editprayer
    #         )
    #     ],
    #     states={
    #         EDIT_PRAYER: [
    #             MessageHandler(
    #                 filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
    #                 editprayer,
    #             )
    #         ],
    #     },
    #     fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    # )
    delprayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "delete", 
                choose_delprayer_mode
            )
        ],
        states={
            CHOOSE_DEL_PRAYER: [
                MessageHandler(
                     filters.Regex("^(Delete Prayer Request)$"),
                    input_del_prayerreq,
                ),
                MessageHandler(
                     filters.Regex("^(Delete Prayer in Prayer Request)$"),
                    input_delprayer_prayerreq,
                )
            ],
            TYPING_DEL_PRAYER_REQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    del_prayer_req,
                )
            ],
            TYPING_DEL_PRAYER_PRAYERREQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    input_delprayer,
                )
            ],
            TYPING_DEL_PRAYER_INDEX: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), end_convo)],
    )
    application.add_handler(prayerreq_conv_handler)
    application.add_handler(prayer_conv_handler)
    application.add_handler(fulfill_conv_handler)
    application.add_handler(addfulfill_conv_handler)
    # application.add_handler(editprayer_conv_handler)
    application.add_handler(delprayer_conv_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    application.run_polling()