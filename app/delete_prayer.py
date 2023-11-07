import constants
from func import text_concat

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler


# ------------------------------------------------------------------------------
# delete prayer
# ------------------------------------------------------------------------------
async def choose_delprayer_mode(update, context):
    """
    Usage: /delete

    Gives user 2 options: Delete a request or delete a prayer in a request

    Returns: constants.CHOOSE_DEL_PRAYER
    """
    reply_keyboard = [["Delete Request", "Delete Prayer in Request"]]
    await update.message.reply_text(
        "Do you want to remove a prayer request or prayer in a prayer request?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Delete prayer or request?",
        ),
    )
    return constants.CHOOSE_DEL_PRAYER


# delete prayer in prayer req
async def input_del_prayerreq(update, context):
    """
    When user selects delete prayer request, returns TYPING_DEL_PRAYER_REQ

    Returns: constants.TYPING_DEL_PRAYER_REQ
    """
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_DEL_PRAYER_REQ


async def del_prayer_req(update, context):
    """
    Delete the prayer request

    Returns: ConversationHandler.END
    """
    prayer_req = update.message.text

    # Check if prayer request exists
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Remove prayer request
    context.chat_data["ongoing"].pop(prayer_req)
    await update.message.reply_text(
        "Prayer request deleted!",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Clear cache
    context.user_data.clear()

    return ConversationHandler.END


# delete prayer req
async def input_delprayer_prayerreq(update, context):
    """
    When user selects delete prayer, returns TYPING_DEL_PRAYER_PRAYERREQ

    Returns: constants.TYPING_DEL_PRAYER_PRAYERREQ
    """
    await update.message.reply_text(
        "What is the prayer request?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.TYPING_DEL_PRAYER_PRAYERREQ


async def input_delprayer(update, context):
    """
    Check if prayer request exist and have prayers
    Provide prayer requests prayers if so

    Returns: ConversationHandler.END
    """
    prayer_req = update.message.text

    # Check if prayer request exists
    if not prayer_req in context.chat_data["ongoing"]:
        await update.message.reply_text(
            "Not able to find prayer request! Try checking your caps!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Check if prayer request has prayers
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

    # Display all prayers of prayer request
    reply = text_concat.create_prayer_text(
        context.chat_data["ongoing"][prayer_req]["prayers"]
    )
    await update.message.reply_text(
        reply,
        reply_markup=ReplyKeyboardRemove(),
    )

    # store this before continuing
    context.user_data["del_prayer_req"] = update.message.text
    return constants.TYPING_DEL_PRAYER_INDEX


async def delprayer(update, context):
    """
    Usage: /delprayer key

    Deletes a prayer in prayer request and returns a response message if deleted
    successfully

    Returns: str
    """
    # because actual numbers start from 1, we deduct the index to start from 0
    index = int(update.message.text) - 1

    # Check if the option is valid
    len_of_prayer_req = len(
        context.chat_data["ongoing"][context.user_data["del_prayer_req"]]
    )
    if index >= len_of_prayer_req or index < 0:
        await update.message.reply_text(
            "Option not available!",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Delete needs to have ["prayers"] due to data structure
    del context.chat_data["ongoing"][context.user_data["del_prayer_req"]]["prayers"][
        index
    ]
    await update.message.reply_text(
        "Deleted prayer point!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END
