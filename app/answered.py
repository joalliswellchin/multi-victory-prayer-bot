import constants
import os
from datetime import datetime

from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler


# ------------------------------------------------------------------------------
# add fulfilled prayer via complete prayer list
# ------------------------------------------------------------------------------
async def input_fulfillprayer(update, context):
    """
    Usage: /answered

    Request for request to be added to fulfilled list

    Returns: constants.FULFILL_PRAYER
    """
    await update.message.reply_text(
        "Which prayer request has been fulfilled?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.FULFILL_PRAYER


async def check_input_fulfillprayer(update, context):
    """
    Check and add request and its info into fulfilled list, then add the time it
    was added

    Returns: update.message.reply_text OR ConversationHandler.END
    """
    # Check if request exists
    prayer_req = update.message.text
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # add prayer request to fulfilled list
    context.chat_data["fulfilled"][prayer_req] = context.chat_data["ongoing"][
        prayer_req
    ]
    context.chat_data["fulfilled"][prayer_req][
        "fulfilled_time"
    ] = update.message.date.strftime(os.environ.get("DATETIME_FORMAT"))

    # remove prayer request from request list, then clean up conversation data
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
    """
    Usage: /imanswered

    Adding directly to fulfilled list

    Returns: constants.ADD_FULFILL_PRAYER
    """
    await update.message.reply_text("What is the prayer that was answered?")
    return constants.ADD_FULFILL_PRAYER


async def addfulfillprayer(update, context):
    """
    Check if answered prayer exists in fulfilled list, then add the prayer with
    time

    Returns: update.message.reply_text OR ConversationHandler.END
    """
    answered_prayer = update.message.text

    # check if the prayer fulfilled exists
    if answered_prayer in context.chat_data["fulfilled"]:
        await update.message.reply_text(
            "Prayer request already exists! Double blessings for you!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # add fulfilled prayer directly and include the time
    context.chat_data["fulfilled"][answered_prayer] = {
        "prayers": list(),
        "fulfilled_time": update.message.date.strftime(
            os.environ.get("DATETIME_FORMAT")
        ),
    }
    await update.message.reply_text("Added answered prayer!")
