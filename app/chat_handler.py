from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.ext import (
    ContextTypes,
)
from typing import Optional, Tuple


# taken from https://docs.python-telegram-bot.org/en/v20.6/examples.chatmemberbot.html
def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    """
    Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )
    print("chat_member_update", chat_member_update)
    print("status_change", status_change)
    print("old_is_member", old_is_member)
    print("new_is_member", new_is_member)

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Tracks the chats the bot is in.
    """
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name
    print("cause_name", cause_name)

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        print("in here")
        print(was_member)
        print(is_member)
        if not was_member and is_member:
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif not was_member and is_member:
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
    elif was_member and not is_member:
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
