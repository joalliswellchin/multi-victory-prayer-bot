"""
This file is to help form messages or responses.

This is because telegram has some limitations to the number of characters it 
can have in 1 message, and it is currently not automatic
"""


from typing import Dict, List


def create_prayer_text(texts: List):
    """
    Forms a prayer string

    Sample input:
    [
        {
            "time": "%d/%m/%Y, %H:%M:%S",
            "prayer": "prayer text"
        }
    ]

    Returns: String

    Sample return:
    index: time - prayer
    """
    text_list = ""
    if len(texts) == 0:
        text_list += "<i>Not prayed yet</i>\n"
    for index, prayer_info in enumerate(texts):
        text_list += "{}: {} - {}\n".format(
            index + 1, prayer_info["time"], prayer_info["prayer"]
        )
    return text_list


def create_prayer_list_text(prayer_list: Dict):
    """
    Forms a prayer request to prayer string

    Returns: String

    Sample return:
    **request_1**
    1: prayer_1

    **request_2**
    2: prayer_2
    """
    replies = []
    prayer_info = ""
    for k, v in prayer_list:
        v_list = create_prayer_text(v["prayers"])

        # check if it exceeds message length
        # if exceed add to replies and then reset
        # NOTE: This is hardcoded value for now
        to_add = "\n<b>{}</b> \n{}".format(k, v_list)
        if len(prayer_info) + len(to_add) > 2000:
            replies.append(prayer_info)
            prayer_info = to_add
        else:
            prayer_info += to_add
    # ensure the last text is also added
    # if empty, dont add so that it will cover for replies that are empty to be
    # of 0 len
    if len(prayer_info) > 0:
        replies.append(prayer_info)
    return replies


def create_request_list_text(prayer_list: Dict):
    """
    Forms a prayer request to prayer string

    Returns: String

    Sample return:
    **request_1**

    **request_2**
    """
    replies = []
    prayer_info = ""
    for k, _ in prayer_list:
        # check if it exceeds message length
        # if exceed add to replies and then reset
        # NOTE: This is hardcoded value for now
        to_add = "\n<b>{}</b>\n".format(k)
        if len(prayer_info) + len(to_add) > 2000:
            replies.append(prayer_info)
            prayer_info = to_add
        else:
            prayer_info += to_add
    # ensure the last text is also added
    # if empty, dont add so that it will cover for replies that are empty to be
    # of 0 len
    if len(prayer_info) > 0:
        replies.append(prayer_info)
    return replies
