import constants

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler
from telegram.constants import ParseMode

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