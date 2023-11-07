import constants
import os
from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler


# ------------------------------------------------------------------------------
# add prayer
# ------------------------------------------------------------------------------
async def input_prayer_req(update, context):
    """
    Usage: /request

    Send user a message for new request

    Returns: constants.TYPING_PRAYER_REQ
    """
    # Generate ID by getting the last number and add 1
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_PRAYER_REQ


async def check_input_prayer_req(update, context):
    """
    Check if request exists
    If request exists, ask if prayer added is wanted

    Returns: ConversationHandler.END OR constants.NEXT_PRAYER
    """
    # This 64 characters is the limit of InlineKeyboard, later used in pick_request
    if len(update.message.text) >= 64:
        await update.message.reply_text(
            "Please type in a prayer request in less than 64 characters"
        )
        return ConversationHandler.END

    # Check if prayer request exists
    if update.message.text in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Prayer request already exists! Edit prayer or delete if you require",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:  # if prayer request does not exist, request for prayer and add metadata
        reply_keyboard = [["Yes", "Not now"]]
        # store this for continuing
        context.user_data["prayer_req"] = update.message.text
        # context.chat_data["ongoing"][update.message.text] = list()
        context.chat_data["ongoing"][update.message.text] = {
            "tags": list(),
            "prayers": list(),
            "time": datetime.now().strftime(os.environ.get("DATETIME_FORMAT")),
        }
        await update.message.reply_text(
            "Prayer request added. Would you like to continue adding a prayer?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Complete Prayer?",
            ),
        )
        return constants.NEXT_PRAYER


async def complete_prayer_req(update, context):
    """
    Send user a message for prayer

    Return: constants.TYPING_PRAYER
    """
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_PRAYER
