# import constants
from func import text_concat

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler
from telegram.constants import ParseMode


# ------------------------------------------------------------------------------
# Display functions
# ------------------------------------------------------------------------------
async def list_request(update, context):
    """
    Usage: /listrequest

    Show all prayer requests (ongoing and value == "")
    """
    # Get all prayer request without prayer
    # prayer requests without prayer is ["prayers"] with only empty list
    untracked = {
        k: v
        for k, v in context.chat_data["ongoing"].items()
        if not len(v["prayers"]) > 0
    }
    # replies = text_concat.create_request_list_text(untracked.items())
    # We use empty_text = "" to create only the requests in the message
    replies = text_concat.create_prayer_list_text(untracked.items(), empty_text="")

    # If there is no prayer requests, show that different message
    if len(replies) == 0:
        text = "No prayer request! Go ask leh~"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    else:
        for reply in replies:
            await update.message.reply_text(reply, parse_mode=ParseMode.HTML)


async def pick_request(update, context):
    """
    Usage: /pickrequest

    Show all prayer requests as a button
    """
    # Check if there is prayer requests
    if len(context.chat_data["ongoing"].items()) == 0:
        await update.message.reply_text("No prayer requests! Go ask leh~")
        return ConversationHandler.END

    # TODO: fix inline keyboard to have previous and next buttons
    # TODO: Change item_per_row to env and set it to 1, and change to items_to_display
    # Get all requests and make them InlineKeyboardButton
    all_items = [
        InlineKeyboardButton(k, callback_data=k)
        for k, _ in context.chat_data["ongoing"].items()
    ]

    # Form rows for display
    inline_keyboard = list()
    row = list()
    item_per_row = 3
    for index, item in enumerate(all_items):
        row.append(item)
        if index % item_per_row == item_per_row - 1:
            inline_keyboard.append(row)
            row = list()
    if len(row) > 0:  # add leftover of row to last row
        inline_keyboard.append(row)

    await update.message.reply_text(
        "Which prayer request you want to show?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )


async def picked_request_prayer_list(update, context):
    """
    Usage: None

    Shows prayers of prayer request, after /pickrequest
    """
    # Get selected InlineKeyboardButton
    query = update.callback_query
    await query.answer()
    prayer_list = context.chat_data["ongoing"][query.data]
    prayer = text_concat.create_prayer_text(prayer_list["prayers"])

    # Return prayer request and then prayers
    await query.edit_message_text(query.data)
    await update.effective_chat.send_message(prayer)


async def list_all(update, context):
    """
    Usage: /listall

    Show all prayer (untracked and completed)
    """
    new_list = context.chat_data["ongoing"].items()

    # Get all prayer requests in array and send them in multiple messages
    replies = text_concat.create_prayer_list_text(new_list)
    if len(replies) == 0:
        text = "No prayers or requests! Pray leh~"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    for reply in replies:
        await update.message.reply_text(reply, parse_mode=ParseMode.HTML)


async def list_pray(update, context):
    """
    Usage: /listpray

    Show all completed prayer (ongoing and value that is not empty)
    """
    # Get all prayer request without prayer
    # prayer requests with prayer is ["prayers"] with non-empty list
    completed = {
        k: v for k, v in context.chat_data["ongoing"].items() if len(v["prayers"]) > 0
    }

    # Get all prayer info in array and send them in multiple messages
    replies = text_concat.create_prayer_list_text(completed.items())
    if len(replies) == 0:
        text = "No prayers! Pray leh~"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    for reply in replies:
        await update.message.reply_text(reply, parse_mode=ParseMode.HTML)


async def list_answered(update, context):
    """
    Usage: /listanswered

    Show all prayers that have been answered
    """
    # Get all answered prayers in array and send them in multiple messages
    replies = text_concat.create_prayer_list_text(
        context.chat_data["fulfilled"].items(), empty_text=""
    )
    if len(replies) == 0:
        text = "No answered prayers! Don't give up hope!"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    for reply in replies:
        await update.message.reply_text(reply, parse_mode=ParseMode.HTML)
