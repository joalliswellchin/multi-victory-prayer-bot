"""
This set of commands is to help produce a document for a review of all prayers

A review process will consist of:
1. Generating a report
2. Ask for approval to remove fulfilled prayers
3. Remove temp document regardless of response
4. If 2. is no, keep fulfilled prayers. If yes, reset fulfilled prayers
"""

import constants

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler


async def doc_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate document of all fulfilled prayers

    Returns: constants.GENERATE_DOCUMENT
    """
    # generate the file
    # TODO: main_doc_gen_flow(chat_id) or relevent id
    # TODO: consider using markdown instead of PDF. Go for easier function first
    # and consider generating mermaidjs compatible information

    # https://stackoverflow.com/questions/70298050/how-to-send-a-document-with-telegram-bot
    # TODO: remove temporary file test.pdf from temp/ folder
    chat_id = update.message.chat_id
    document = open("temp/test.pdf", "rb")
    await context.bot.send_document(chat_id, document)

    # TODO: then delete temporary file

    await update.message.reply_text(
        "Do you want to restart your fulfilled prayers?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return constants.GENERATE_DOCUMENT


async def doc_gen_remove_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove fulfilled prayers after generated document review sent

    Returns: ConversationHandler.END
    """
    # Send message
    await update.message.reply_text(
        "Okay! Be encouraged today by this victories you partnered with God!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def end_doc_gen_convo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provide message when ending a conversation about document generation

    Returns: ConversationHandler.END
    """
    # Send message
    await update.message.reply_text(
        "Okay! Be encouraged today by this victories you partnered with God!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ------------------------------------------------------------------------------
# Creating Summary document
# ------------------------------------------------------------------------------


def main_doc_gen_flow(chat_id):
    # Create temporary file
    # Then get all fulfilled requests and their prayers
    # Get the date, and get the year
    # Then get count total requests
    # Finally get all info and put into temporary file
    return
