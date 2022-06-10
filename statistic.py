from datetime import datetime


def get_stat_dict(user_stat):
    return vars(user_stat)


def get_unix_time_from_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0


def get_time_from_unix_time(ms):
    return datetime.fromtimestamp(ms / 1000.0)
