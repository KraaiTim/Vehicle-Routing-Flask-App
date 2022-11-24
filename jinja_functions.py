import time


def seconds_to_time(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    if hour == 0:
        formatted_time = time.strftime("%#M:%S", time.gmtime(seconds))
    else:
        formatted_time = time.strftime("%#H:%M:%S", time.gmtime(seconds))

    return formatted_time
