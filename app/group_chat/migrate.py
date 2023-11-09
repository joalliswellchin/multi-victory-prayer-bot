async def migrate_chat(update, context):
    """
    duplicate all info into new chat when moved to SUPER_GROUP

    Returns: None
    """
    old_chat_id = update.message.chat.id
    new_chat_id = update.message.migrate_to_chat_id
    if old_chat_id != None and new_chat_id != None:
        application = context.application
        application.migrate_chat_data(old_chat_id=old_chat_id, new_chat_id=new_chat_id)
