"""
PRIVATE CHAT DATA STRUCTURE:
context.chat_data = {
    "ongoing": {
        "req": {
            "prayers": [
                {
                    "prayer": str,
                    "time": str,
                }
            ],
            "time" str,
            "tags": [str]
        }
    },
    "fulfilled": {
        "req": {
            "prayers": [
                {
                    "prayer": str,
                    "time": str,
                }
            ],
            "time" str,
            "fulfilled_time": str,
            "tags": [str],
        }
    }
    "tags": [str]
}
context.user_data = {
    "prayer_req": str
}

GROUP DATA STRUCTURE:
context.chat_data = {
    "ongoing": {
        "req": {
            "prayers": [
                {
                    "prayer": str,
                    "time": str,
                }
            ],
            "time" str,
            "tags": [str]
            "req_name": str,
            "req_user": str,
        }
    },
    "fulfilled": {
        "req": {
            "prayers": [
                {
                    "prayer": str,
                    "time": str,
                }
            ],
            "time" str,
            "fulfilled_time": str,
            "tags": [str],
            "req_name": str,
            "req_user": str,
        }
    }
    "tags": [str]
}
context.user_data = {
    "prayer_req": str
}

Other notes:
- Completed prayers are prayers with prayer requests and prayer not blank
- Placing all in one file to make this easier for copy pasta as of now (and other architecture mini-concerns)
- Not building prayer requests editing because it should be intended to delete over editing
- context.userdata is only for temporary data within a conversation
"""

# from datetime import datetime
import logging
import os

from dotenv import load_dotenv

load_dotenv(os.path.dirname(os.path.realpath(__file__)) + "/.env")

# import mongodb_conn as conn
import constants
import list_prayer
import request_prayer
import pray
import delete_prayer
import answered
import common

from group_chat.migrate import migrate_chat
from group_chat.start import group_start, group_add

from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    PicklePersistence,
    ConversationHandler,
    CallbackQueryHandler,
)

from mongopersistence import MongoPersistence

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Default for LOCAL and any other env
    application = (
        ApplicationBuilder()
        .token(os.environ.get("TELEGRAM_API_KEY"))
        .concurrent_updates(True)
        .build()
    )

    # Create application with pickle file reference and pass it to bot token
    if os.environ.get("ENV") == "UAT":
        # TODO: Set up for UAT
        print("UAT not available")
    elif os.environ.get("ENV") == "PROD":
        # TODO: Set up for PROD
        print("PROD not available")
    elif os.environ.get("ENV") == "LOCAL" and os.environ.get("DB_ENV") == "LOCAL_FILE":
        persistence = PicklePersistence(
            filepath=os.path.dirname(os.path.realpath(__file__))
            + "/assets/saved_convo",
            single_file=False,
        )
        application = (
            ApplicationBuilder()
            .token(os.environ.get("TELEGRAM_API_KEY"))
            .concurrent_updates(True)
            .persistence(persistence)
            .build()
        )
    elif os.environ.get("ENV") == "LOCAL" and os.environ.get("DB_ENV") == "MONGO":
        application = (
            ApplicationBuilder().token(os.environ.get("TELEGRAM_API_KEY")).build()
        )
        # conn.client
    elif (
        os.environ.get("ENV") == "LOCAL" and os.environ.get("DB_ENV") == "MONGO_PERSIST"
    ):
        MONGODB_USER = os.environ.get("MONGODB_USER")
        MONGODB_PWD = os.environ.get("MONGODB_PWD")
        MONGODB_CLUSTER = os.environ.get("MONGODB_CLUSTER")
        # uri = "mongodb://username:password@your-ip:27017/"
        uri = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@{MONGODB_CLUSTER}.dnv17te.mongodb.net/?retryWrites=true&w=majority"
        persistence = MongoPersistence(
            mongo_url=uri,
            db_name=os.environ.get("MONGODB_DBNAME"),
            name_col_user_data=os.environ.get("MONGODB_USER_DATA"),  # optional
            name_col_chat_data=os.environ.get("MONGODB_CHAT_DATA"),  # optional
            name_col_bot_data=os.environ.get("MONGODB_BOT_DATA"),  # optional
            name_col_conversations_data=os.environ.get("MONGODB_CONVO"),  # optional
            create_col_if_not_exist=True,  # optional
            # ignore_general_data=["cache"],
            # ignore_user_data=["foo", "bar"],
            load_on_flush=False,
            update_interval=int(os.environ.get("MONGODB_UPLOAD_INTERVAL", "600")),
        )
        application = (
            ApplicationBuilder()
            .token(os.environ.get("TELEGRAM_API_KEY"))
            .concurrent_updates(True)
            .persistence(persistence)
            .build()
        )

    # All commands added here
    start_handler = CommandHandler("start", common.start)
    help_cmd_handler = CommandHandler("help", common.help)
    showunprayed_cmd_handler = CommandHandler("listrequest", list_prayer.list_request)
    showall_cmd_handler = CommandHandler("listall", list_prayer.list_all)
    showprayed_cmd_handler = CommandHandler("listpray", list_prayer.list_pray)
    showvictory_cmd_handler = CommandHandler("listanswered", list_prayer.list_answered)

    # Adding handlers to application builder
    application.add_handler(
        MessageHandler(filters.StatusUpdate.CHAT_CREATED, group_start)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_add)
    )
    application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chat))
    application.add_handler(start_handler)
    application.add_handler(help_cmd_handler)
    application.add_handler(showunprayed_cmd_handler)
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
                ),
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
        entry_points=[CommandHandler("pray", pray.input_complete_prayer_req)],
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
    fulfill_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("answered", answered.input_fulfillprayer)],
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
        entry_points=[CommandHandler("imanswered", answered.input_addfulfillprayer)],
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
        entry_points=[CommandHandler("delete", delete_prayer.choose_delprayer_mode)],
        states={
            constants.CHOOSE_DEL_PRAYER: [
                MessageHandler(
                    filters.Regex("^(Delete Request)$"),
                    delete_prayer.input_del_prayerreq,
                ),
                MessageHandler(
                    filters.Regex("^(Delete Prayer in Request)$"),
                    delete_prayer.input_delprayer_prayerreq,
                ),
                MessageHandler(
                    filters.Regex("^(Delete Answered Prayer)$"),
                    delete_prayer.input_del_answered,
                ),
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
            constants.TYPING_DEL_ANSWERED: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    delete_prayer.del_answered,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    showprayerrequest_cmd_handler = ConversationHandler(
        entry_points=[CommandHandler("pickrequest", list_prayer.pick_request)],
        states={
            constants.DISPLAY_PICKED_PRAYER: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^EXIT$")),
                    list_prayer.picked_request_prayer_list,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^EXIT$"), common.end_convo)],
    )
    application.add_handler(prayerreq_conv_handler)
    application.add_handler(prayer_conv_handler)
    application.add_handler(fulfill_conv_handler)
    application.add_handler(addfulfill_conv_handler)
    application.add_handler(showprayerrequest_cmd_handler)
    application.add_handler(delprayer_conv_handler)

    # Handle all other commands that are not recognised
    unknown_handler = MessageHandler(filters.COMMAND, common.unknown)
    application.add_handler(unknown_handler)

    # Convenient app starting function
    application.run_polling()
