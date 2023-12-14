import constants
from func import text_concat

# from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    # and check if message is from a group
    is_private = update.message.chat.type == "private"
    replies = text_concat.create_prayer_list_text(
        untracked.items(), empty_text="", is_private=is_private
    )

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
        await update.message.reply_text(
            "No prayer requests! Go ask leh~",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    # uncomment segment for InlineKeyboard display and import statements
    # # TODO: fix inline keyboard to have previous and next buttons
    # # TODO: Change item_per_row to env and set it to 1, and change to items_to_display
    # # Get all requests and make them InlineKeyboardButton
    # all_items = [
    #     InlineKeyboardButton(k, callback_data=k)
    #     for k, _ in context.chat_data["ongoing"].items()
    # ]
    # # Form rows for display
    # inline_keyboard = list()
    # row = list()
    # item_per_row = 3
    # for index, item in enumerate(all_items):
    #     row.append(item)
    #     if index % item_per_row == item_per_row - 1:
    #         inline_keyboard.append(row)
    #         row = list()
    # if len(row) > 0:  # add leftover of row to last row
    #     inline_keyboard.append(row)
    # await update.message.reply_text(
    #     "Which prayer request you want to show?",
    #     reply_markup=InlineKeyboardMarkup(inline_keyboard),
    # )

    reply_keyboard = [[k] for k, _ in context.chat_data["ongoing"].items()]
    reply_keyboard.append(["EXIT"])
    await update.message.reply_text(
        "Which prayer request you want to show?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Pick a prayer request",
        ),
    )
    return constants.DISPLAY_PICKED_PRAYER


async def picked_request_prayer_list(update, context):
    """
    Usage: None

    Shows prayers of prayer request, after /pickrequest
    """
    # uncomment segment for InlineKeyboard display and import statements
    # # Get selected InlineKeyboardButton
    # query = update.callback_query
    # await query.answer()
    # prayer_list = context.chat_data["ongoing"][query.data]
    # prayer = text_concat.create_prayer_text(prayer_list["prayers"])
    # # Return prayer request and then prayers
    # await query.edit_message_text(query.data)
    # await update.effective_chat.send_message(prayer)

    # return prayer request and it's prayer contents
    query = update.message.text
    prayer_list = context.chat_data["ongoing"][query]
    prayer = text_concat.create_prayer_text(prayer_list["prayers"])
    await update.message.reply_text(
        query,
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.effective_chat.send_message(prayer, parse_mode=ParseMode.HTML)


async def list_all(update, context):
    """
    Usage: /listall

    Show all prayer (untracked and completed)
    """
    new_list = context.chat_data["ongoing"].items()

    # Check if message is from a group
    is_private = update.message.chat.type == "private"
    # Get all prayer requests in array and send them in multiple messages
    replies = text_concat.create_prayer_list_text(new_list, is_private=is_private)
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

    # Check if message is from a group
    is_private = update.message.chat.type == "private"
    # Get all prayer info in array and send them in multiple messages
    replies = text_concat.create_prayer_list_text(
        completed.items(), is_private=is_private
    )
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
    # Check if message is from a group
    is_private = update.message.chat.type == "private"
    # Get all answered prayers in array and send them in multiple messages
    replies = text_concat.create_answered_prayer_list_text(
        context.chat_data["fulfilled"].items(),
        empty_text="",
        is_private=is_private,
    )
    if len(replies) == 0:
        text = "No answered prayers! Don't give up hope!"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    for reply in replies:
        await update.message.reply_text(reply, parse_mode=ParseMode.HTML)
