import constants

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

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
    return constants.TYPING_PRAYER_REQ

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
        return constants.NEXT_PRAYER

async def complete_prayer_req(update, context):
    await update.message.reply_text(
        "What is the prayer?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_PRAYER
