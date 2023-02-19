def replace_newline(text):
    """\n => split"""
    return text.split('\n')

def time_print(time):
    if not time:
        return None
    now_time = "{0:%m/%d/%H:%M}".format(time)
    return now_time

def message_view_length(message):
    if len(message) < 15:
        return message
    return message[:15] + '…'