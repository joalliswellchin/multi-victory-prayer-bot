import constants

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

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
    return constants.CHOOSE_DEL_PRAYER

# delete prayer in prayer req
async def input_del_prayerreq(update, context):
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_DEL_PRAYER_REQ

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
    return constants.TYPING_DEL_PRAYER_PRAYERREQ

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
    return constants.TYPING_DEL_PRAYER_INDEX

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
