import common
import os


async def group_start(update, context):
    """
    Start automatically when created with group chat
    This function is here to avoid creation of
    update.message.supergroup_chat_created as that should be under migration

    Returns None
    """
    if update.message.group_chat_created or update.message.channel_chat_created:
        await common.start(update, context)


async def group_add(update, context):
    """
    Start automatically when added to group chat
    This function is here as update.message.group_chat_created is only True when
    bot is created at the start, and not adhoc added to the group

    Returns None
    """
    chat_user_info = update.message.new_chat_members[0]
    bot_id = os.environ.get("TELEGRAM_API_KEY").split(":")[0]
    if str(chat_user_info.id) == bot_id and chat_user_info.is_bot:
        await common.start(update, context)
