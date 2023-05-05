import constants
from datetime import datetime

from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

# ------------------------------------------------------------------------------
# add fulfilled prayer via complete prayer list
# ------------------------------------------------------------------------------
async def input_fulfillprayer(update, context):
    """Usage: /fulfillprayer"""
    await update.message.reply_text(
        "Which prayer request has been fulfilled?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.FULFILL_PRAYER

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
    return constants.ADD_FULFILL_PRAYER

async def addfulfillprayer(update, context):
    answered_prayer = update.message.text
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    context.chat_data["fulfilled"][now + " - " + answered_prayer] = list()
    await update.message.reply_text("Added answered prayer!")
