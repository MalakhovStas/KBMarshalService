from datetime import datetime, timedelta


def get_time_left():
    """ Функция возвращает дни, часы, минуты и секунды оставшиеся до конца текущего дня """
    end_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_left = end_of_day - datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds
