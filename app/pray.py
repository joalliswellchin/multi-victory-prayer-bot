import constants

from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler


# ------------------------------------------------------------------------------
# add completed prayer
# ------------------------------------------------------------------------------
# this is to get context if not from addprayer
async def input_complete_prayer_req(update, context):
    """
    Usage: /pray

    Adding prayer to existing request
    Sends user a message for existing request

    Returns: constants.COMPLETE_PRAYER
    """
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.COMPLETE_PRAYER


async def check_complete_prayer_req(update, context):
    """
    Adding prayer

    Returns: ConversationHandler.END OR constants.TYPING_PRAYER
    """
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

    # Check if request exists
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

    return constants.TYPING_PRAYER
