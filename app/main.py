"""
Data structures:
context.chatdata = {
    "ongoing": {
        "req": [str]
    },
    "fulfilled": {
        "req": [str]
    }
}
context.userdata = {
    "prayer_req": str
}

Other notes:
- Completed prayers are prayers with prayer requests and prayer not blank
- Placing all in one file to make this easier for copy pasta as of now (and other architecture mini-concerns)
- Not building prayer requests editing because it should be intended to delete over editing
- context.userdata is only for temporary data within a conversation
"""

from datetime import datetime
import logging
import os

import constants
import list_prayer
import request_prayer
import pray
import delete_prayer
import answered
import common

from dotenv import load_dotenv
from telegram.ext import (filters, MessageHandler, ApplicationBuilder, 
CommandHandler, PicklePersistence, ConversationHandler, 
CallbackQueryHandler)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv(os.path.dirname(os.path.realpath(__file__)) + "/.env")

# Just to test handler
def lambda_handler(event, context):
    message = 'Hello, world!'
    return {
        'statusCode': 200,
        'body': message
    }

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).build()

    # Create application with pickle file reference and pass it to bot token
    persistence = PicklePersistence(
        filepath=os.path.dirname(os.path.realpath(__file__)) + "/assets/saved_convo", 
        single_file=False,
    )
    application = ApplicationBuilder().token(os.environ["TELEGRAM_API_KEY"]).persistence(persistence).build()
    
    # All commands added here
    start_handler = CommandHandler('start', common.start)
    help_cmd_handler = CommandHandler('help', common.help)
    showunprayed_cmd_handler = CommandHandler('listrequest', list_prayer.showunprayed)
    showprayerrequest_cmd_handler = CommandHandler('pickrequest', list_prayer.showprayerrequest)
    showall_cmd_handler = CommandHandler('listall', list_prayer.showall)
    showprayed_cmd_handler = CommandHandler('listpray', list_prayer.showprayed)
    showvictory_cmd_handler = CommandHandler('listanswered', list_prayer.showvictory)
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(showunprayed_cmd_handler)
    application.add_handler(showprayerrequest_cmd_handler)
    application.add_handler(CallbackQueryHandler(list_prayer.showprayerrequest_prayers))
    application.add_handler(showall_cmd_handler)
    application.add_handler(showprayed_cmd_handler)
    application.add_handler(showvictory_cmd_handler)
    
    # Allow commands to be also receivable in text
    # help_msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)
    prayerreq_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("request", request_prayer.input_prayer_req)],
        states={
            constants.TYPING_PRAYER_REQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    request_prayer.check_input_prayer_req,
                )
            ],
            constants.NEXT_PRAYER: [
                MessageHandler(
                     filters.Regex("^(Yes)$"),
                    request_prayer.complete_prayer_req,
                ),
                MessageHandler(
                     filters.Regex("^(Not now)$"),
                    common.end_request_convo,
                )
            ],
            constants.TYPING_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    common.addprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    prayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "pray", 
                pray.input_complete_prayer_req
            )
        ],
        states={
            constants.COMPLETE_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    pray.check_complete_prayer_req,
                )
            ],
            constants.TYPING_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    common.addprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    #TODO: Complete these flow
    fulfill_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "answered", 
                answered.input_fulfillprayer
            )
        ],
        states={
            constants.FULFILL_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    answered.check_input_fulfillprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    addfulfill_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "imanswered", 
                answered.input_addfulfillprayer
            )
        ],
        states={
            constants.ADD_FULFILL_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    answered.addfulfillprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    delprayer_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "delete", 
                delete_prayer.choose_delprayer_mode
            )
        ],
        states={
            constants.CHOOSE_DEL_PRAYER: [
                MessageHandler(
                     filters.Regex("^(Delete Prayer Request)$"),
                    delete_prayer.input_del_prayerreq,
                ),
                MessageHandler(
                     filters.Regex("^(Delete Prayer in Prayer Request)$"),
                    delete_prayer.input_delprayer_prayerreq,
                )
            ],
            constants.TYPING_DEL_PRAYER_REQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delete_prayer.del_prayer_req,
                )
            ],
            constants.TYPING_DEL_PRAYER_PRAYERREQ: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delete_prayer.input_delprayer,
                )
            ],
            constants.TYPING_DEL_PRAYER_INDEX: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delete_prayer.delprayer,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    application.add_handler(prayerreq_conv_handler)
    application.add_handler(prayer_conv_handler)
    application.add_handler(fulfill_conv_handler)
    application.add_handler(addfulfill_conv_handler)
    # application.add_handler(editprayer_conv_handler)
    application.add_handler(delprayer_conv_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, common.unknown)
    application.add_handler(unknown_handler)
    application.run_polling()